from dataclasses import dataclass
from math import ceil

from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import Candidate, Decision
from app.models.enums import CandidateSignal, CandidateState, DecisionValue
from app.schemas.workflow import BatchDecisionCreate, DecisionCreate
from app.services import action_executor
from app.services.classifier import classify_demo_candidate
from app.services.demo_candidates import DEMO_CANDIDATES
from app.services.ownership import get_or_create_local_alpha_user


class HumanApprovalRequiredError(ValueError):
    pass


class CandidateNotFoundError(LookupError):
    pass


@dataclass
class PaginationResult:
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_previous: bool
    has_next: bool


@dataclass
class SourceListResult:
    items: list[Candidate]
    pagination: PaginationResult
    available_categories: list[str]


@dataclass
class DecisionWriteResult:
    decision: Decision
    applied: bool


@dataclass
class BatchDecisionResult:
    applied: list[Decision]
    unchanged: list[Decision]


def ensure_demo_candidates(db: Session) -> None:
    user = get_or_create_local_alpha_user(db)
    existing_count = db.scalar(
        select(func.count()).select_from(Candidate).where(Candidate.user_id == user.id)
    )
    if existing_count:
        return user

    for seed in DEMO_CANDIDATES:
        classification = classify_demo_candidate(
            sender_name=seed.source_name,
            sender_email=seed.sender_emails[0],
            subject=seed.representative_subject,
            mailbox_category=seed.mailbox_category,
        )
        db.add(
            Candidate(
                user_id=user.id,
                source_key=seed.source_key,
                source_name=seed.source_name,
                sender_emails=list(seed.sender_emails),
                email_count=seed.email_count,
                representative_subject=seed.representative_subject,
                mailbox_category=seed.mailbox_category,
                candidate_reason=classification.reason,
                classifier_signal=classification.signal,
                suggested_decision=classification.suggested_decision,
                confidence=classification.confidence,
                processing_state=CandidateState.pending_review,
            )
        )

    db.commit()
    return user


def list_sources(
    db: Session,
    *,
    include_processed: bool = False,
    page: int = 1,
    page_size: int = 5,
    search: str | None = None,
    category: str | None = None,
    signal: CandidateSignal | None = None,
) -> SourceListResult:
    user = ensure_demo_candidates(db)

    base_filters = [Candidate.user_id == user.id]
    if not include_processed:
        base_filters.append(Candidate.processing_state == CandidateState.pending_review)

    normalized_search = search.strip() if search else ""
    if normalized_search:
        term = f"%{normalized_search}%"
        base_filters.append(
            or_(
                Candidate.source_name.ilike(term),
                Candidate.representative_subject.ilike(term),
                cast(Candidate.sender_emails, String).ilike(term),
            )
        )

    if signal is not None:
        base_filters.append(Candidate.classifier_signal == signal)

    filters = list(base_filters)
    if category:
        filters.append(Candidate.mailbox_category == category)

    total_items = (
        db.scalar(select(func.count()).select_from(Candidate).where(*filters)) or 0
    )
    total_pages = max(1, ceil(total_items / page_size))
    current_page = min(page, total_pages)
    offset = (current_page - 1) * page_size

    available_categories = list(
        db.scalars(
            select(Candidate.mailbox_category)
            .where(*base_filters)
            .distinct()
            .order_by(Candidate.mailbox_category.asc())
        ).all()
    )

    statement = (
        select(Candidate)
        .options(selectinload(Candidate.decisions))
        .where(*filters)
        .order_by(Candidate.email_count.desc(), Candidate.id.asc())
        .offset(offset)
        .limit(page_size)
    )

    return SourceListResult(
        items=list(db.scalars(statement).all()),
        pagination=PaginationResult(
            page=current_page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_previous=current_page > 1,
            has_next=current_page < total_pages,
        ),
        available_categories=available_categories,
    )


def list_decisions(db: Session) -> list[Decision]:
    user = ensure_demo_candidates(db)

    statement = (
        select(Decision)
        .options(selectinload(Decision.candidate).selectinload(Candidate.decisions))
        .where(Decision.user_id == user.id)
        .order_by(Decision.created_at.desc(), Decision.id.desc())
    )
    return list(db.scalars(statement).all())


def record_decision(db: Session, payload: DecisionCreate) -> DecisionWriteResult:
    user = ensure_demo_candidates(db)

    if not payload.confirmed:
        raise HumanApprovalRequiredError(
            "Explicit human confirmation is required before a decision is recorded."
        )

    candidate = _get_source_or_raise(db, payload.source_id, user.id)

    result = _apply_decision(
        db,
        candidate=candidate,
        decision_value=payload.decision,
        note=payload.note,
    )
    if result.applied:
        db.commit()

    return DecisionWriteResult(
        decision=_load_decision(db, result.decision.id, user.id),
        applied=result.applied,
    )


def record_batch_decision(
    db: Session,
    payload: BatchDecisionCreate,
) -> BatchDecisionResult:
    user = ensure_demo_candidates(db)

    if not payload.confirmed:
        raise HumanApprovalRequiredError(
            "Explicit human confirmation is required before a decision is recorded."
        )

    source_ids = list(dict.fromkeys(payload.source_ids))
    sources = list(
        db.scalars(
            select(Candidate).where(
                Candidate.id.in_(source_ids),
                Candidate.user_id == user.id,
            )
        ).all()
    )
    sources_by_id = {source.id: source for source in sources}
    missing_id = next(
        (source_id for source_id in source_ids if source_id not in sources_by_id), None
    )
    if missing_id is not None:
        raise CandidateNotFoundError(f"Source {missing_id} was not found.")

    applied_ids: list[int] = []
    unchanged_ids: list[int] = []
    for source_id in source_ids:
        result = _apply_decision(
            db,
            candidate=sources_by_id[source_id],
            decision_value=payload.decision,
            note=payload.note,
        )
        if result.applied:
            applied_ids.append(result.decision.id)
        else:
            unchanged_ids.append(result.decision.id)

    if applied_ids:
        db.commit()

    return BatchDecisionResult(
        applied=_ordered_decisions(db, applied_ids, user.id),
        unchanged=_ordered_decisions(db, unchanged_ids, user.id),
    )


def _candidate_state_for_decision(decision: DecisionValue) -> CandidateState:
    if decision == DecisionValue.keep_for_now:
        return CandidateState.kept
    if decision == DecisionValue.mark_low_value:
        return CandidateState.marked_low_value
    return CandidateState.action_recommended


def _get_source_or_raise(db: Session, source_id: int, user_id: int) -> Candidate:
    source = db.scalar(
        select(Candidate).where(
            Candidate.id == source_id,
            Candidate.user_id == user_id,
        )
    )
    if source is None:
        raise CandidateNotFoundError(f"Source {source_id} was not found.")
    return source


def _apply_decision(
    db: Session,
    *,
    candidate: Candidate,
    decision_value: DecisionValue,
    note: str | None,
) -> DecisionWriteResult:
    latest = _latest_decision(db, candidate.id)
    if latest is not None and latest.decision == decision_value:
        return DecisionWriteResult(decision=latest, applied=False)

    decision = Decision(
        user_id=candidate.user_id,
        candidate_id=candidate.id,
        revised_from_decision_id=latest.id if latest is not None else None,
        decision=decision_value,
        note=note,
        human_confirmed=True,
        external_action_status=action_executor.build_external_action_status(
            decision_value
        ),
    )
    candidate.processing_state = _candidate_state_for_decision(decision_value)
    db.add(decision)
    db.flush()
    return DecisionWriteResult(decision=decision, applied=True)


def _latest_decision(db: Session, candidate_id: int) -> Decision | None:
    return db.scalar(
        select(Decision)
        .where(Decision.candidate_id == candidate_id)
        .order_by(Decision.id.desc())
        .limit(1)
    )


def _load_decision(db: Session, decision_id: int, user_id: int) -> Decision:
    decision = db.scalar(
        select(Decision)
        .options(selectinload(Decision.candidate).selectinload(Candidate.decisions))
        .where(Decision.id == decision_id, Decision.user_id == user_id)
    )
    if decision is None:
        raise CandidateNotFoundError(
            "Decision could not be reloaded after persistence."
        )
    return decision


def _ordered_decisions(
    db: Session, decision_ids: list[int], user_id: int
) -> list[Decision]:
    if not decision_ids:
        return []
    decisions = list(
        db.scalars(
            select(Decision)
            .options(selectinload(Decision.candidate).selectinload(Candidate.decisions))
            .where(Decision.id.in_(decision_ids), Decision.user_id == user_id)
        ).all()
    )
    by_id = {decision.id: decision for decision in decisions}
    return [by_id[decision_id] for decision_id in decision_ids if decision_id in by_id]
