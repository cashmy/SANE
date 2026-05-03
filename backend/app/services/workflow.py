from dataclasses import dataclass
from math import ceil

from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import Candidate, Decision
from app.models.user import User
from app.models.enums import CandidateSignal, CandidateState, DecisionValue
from app.schemas.workflow import BatchDecisionCreate, DecisionCreate
from app.services import action_executor
from app.services.classifier import classify_demo_candidate
from app.services.demo_candidates import DEMO_CANDIDATES
from app.models.email_account import EmailAccount
from app.services.ownership import (
    get_or_create_local_alpha_email_account,
    get_or_create_local_alpha_user,
)


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
class DecisionListResult:
    items: list[Decision]
    pagination: PaginationResult


@dataclass
class DecisionWriteResult:
    decision: Decision
    applied: bool


@dataclass
class BatchDecisionResult:
    applied: list[Decision]
    unchanged: list[Decision]


def ensure_demo_candidates(db: Session) -> EmailAccount:
    """Ensure the Local ALPHA demo candidates exist and return the local ALPHA email account."""
    user = get_or_create_local_alpha_user(db)
    account = get_or_create_local_alpha_email_account(db, user)
    existing_count = db.scalar(
        select(func.count())
        .select_from(Candidate)
        .where(Candidate.email_account_id == account.id)
    )
    if existing_count:
        return account

    for seed in DEMO_CANDIDATES:
        classification = classify_demo_candidate(
            sender_name=seed.source_name,
            sender_email=seed.sender_emails[0],
            subject=seed.representative_subject,
            mailbox_category=seed.mailbox_category,
        )
        db.add(
            Candidate(
                email_account_id=account.id,
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
    return account


def list_sources(
    db: Session,
    *,
    user: User,
    include_processed: bool = False,
    page: int = 1,
    page_size: int = 5,
    search: str | None = None,
    category: str | None = None,
    signal: CandidateSignal | None = None,
    email_account_id: int | None = None,
) -> SourceListResult:
    account = _get_list_account_or_none(
        db,
        user=user,
        email_account_id=email_account_id,
    )
    if account is None:
        return SourceListResult(
            items=[],
            pagination=_empty_pagination(page_size=page_size),
            available_categories=[],
        )

    base_filters = [Candidate.email_account_id == account.id]
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


def list_decisions(
    db: Session,
    *,
    user: User,
    page: int = 1,
    page_size: int = 5,
    email_account_id: int | None = None,
) -> DecisionListResult:
    account = _get_list_account_or_none(
        db,
        user=user,
        email_account_id=email_account_id,
    )
    if account is None:
        return DecisionListResult(
            items=[],
            pagination=_empty_pagination(page_size=page_size),
        )

    filters = [
        Decision.user_id == account.user_id,
        Decision.candidate.has(Candidate.email_account_id == account.id),
    ]
    total_items = (
        db.scalar(select(func.count()).select_from(Decision).where(*filters)) or 0
    )
    total_pages = max(1, ceil(total_items / page_size))
    current_page = min(page, total_pages)
    offset = (current_page - 1) * page_size

    statement = (
        select(Decision)
        .options(selectinload(Decision.candidate).selectinload(Candidate.decisions))
        .where(*filters)
        .order_by(Decision.created_at.desc(), Decision.id.desc())
        .offset(offset)
        .limit(page_size)
    )
    return DecisionListResult(
        items=list(db.scalars(statement).all()),
        pagination=PaginationResult(
            page=current_page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_previous=current_page > 1,
            has_next=current_page < total_pages,
        ),
    )


def record_decision(
    db: Session,
    *,
    user: User,
    payload: DecisionCreate,
) -> DecisionWriteResult:
    if not payload.confirmed:
        raise HumanApprovalRequiredError(
            "Explicit human confirmation is required before a decision is recorded."
        )

    decision_user_id = _get_decision_user_id(db, user)
    candidate = _get_source_for_user_or_raise(db, payload.source_id, decision_user_id)

    result = _apply_decision(
        db,
        candidate=candidate,
        user_id=decision_user_id,
        decision_value=payload.decision,
        note=payload.note,
    )
    if result.applied:
        db.commit()

    return DecisionWriteResult(
        decision=_load_decision(db, result.decision.id, decision_user_id),
        applied=result.applied,
    )


def record_batch_decision(
    db: Session,
    *,
    user: User,
    payload: BatchDecisionCreate,
) -> BatchDecisionResult:
    if not payload.confirmed:
        raise HumanApprovalRequiredError(
            "Explicit human confirmation is required before a decision is recorded."
        )

    decision_user_id = _get_decision_user_id(db, user)
    source_ids = list(dict.fromkeys(payload.source_ids))
    sources = list(
        db.scalars(
            select(Candidate)
            .join(EmailAccount, Candidate.email_account_id == EmailAccount.id)
            .where(
                Candidate.id.in_(source_ids),
                EmailAccount.user_id == decision_user_id,
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
            user_id=decision_user_id,
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
        applied=_ordered_decisions(db, applied_ids, decision_user_id),
        unchanged=_ordered_decisions(db, unchanged_ids, decision_user_id),
    )


def _candidate_state_for_decision(decision: DecisionValue) -> CandidateState:
    if decision == DecisionValue.keep_for_now:
        return CandidateState.kept
    if decision == DecisionValue.mark_low_value:
        return CandidateState.marked_low_value
    return CandidateState.action_recommended


def _empty_pagination(*, page_size: int) -> PaginationResult:
    return PaginationResult(
        page=1,
        page_size=page_size,
        total_items=0,
        total_pages=1,
        has_previous=False,
        has_next=False,
    )


def _get_source_for_user_or_raise(
    db: Session, source_id: int, user_id: int
) -> Candidate:
    source = db.scalar(
        select(Candidate)
        .join(EmailAccount, Candidate.email_account_id == EmailAccount.id)
        .where(
            Candidate.id == source_id,
            EmailAccount.user_id == user_id,
        )
    )
    if source is None:
        raise CandidateNotFoundError(f"Source {source_id} was not found.")
    return source


def _apply_decision(
    db: Session,
    *,
    candidate: Candidate,
    user_id: int,
    decision_value: DecisionValue,
    note: str | None,
) -> DecisionWriteResult:
    # user_id is passed explicitly (controlled denormalization).
    # Invariant: user_id must equal candidate.email_account.user_id.
    latest = _latest_decision(db, candidate.id)
    if latest is not None and latest.decision == decision_value:
        return DecisionWriteResult(decision=latest, applied=False)

    decision = Decision(
        user_id=user_id,
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


def _get_decision_user_id(db: Session, user: User) -> int:
    if user.is_local_alpha:
        return ensure_demo_candidates(db).user_id
    return user.id


def _get_list_account_or_none(
    db: Session,
    *,
    user: User,
    email_account_id: int | None,
) -> EmailAccount | None:
    if user.is_local_alpha:
        account = ensure_demo_candidates(db)
        if email_account_id is not None and email_account_id != account.id:
            return None
        return account

    if email_account_id is not None:
        return db.scalar(
            select(EmailAccount).where(
                EmailAccount.user_id == user.id,
                EmailAccount.id == email_account_id,
            )
        )

    return _get_first_account_or_none(db, user.id)


def _get_first_account_or_none(db: Session, user_id: int) -> EmailAccount | None:
    return db.scalar(
        select(EmailAccount)
        .where(EmailAccount.user_id == user_id)
        .order_by(EmailAccount.id.asc())
    )
