from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import Candidate, Decision
from app.models.enums import CandidateState, DecisionValue
from app.schemas.workflow import DecisionCreate
from app.services import action_executor
from app.services.classifier import classify_demo_candidate
from app.services.demo_candidates import DEMO_CANDIDATES


class HumanApprovalRequiredError(ValueError):
    pass


class CandidateNotFoundError(LookupError):
    pass


def ensure_demo_candidates(db: Session) -> None:
    existing_count = db.scalar(select(func.count()).select_from(Candidate))
    if existing_count:
        return

    for seed in DEMO_CANDIDATES:
        classification = classify_demo_candidate(
            sender_name=seed.sender_name,
            sender_email=seed.sender_email,
            subject=seed.subject,
            mailbox_category=seed.mailbox_category,
        )
        db.add(
            Candidate(
                sender_name=seed.sender_name,
                sender_email=seed.sender_email,
                subject=seed.subject,
                mailbox_category=seed.mailbox_category,
                candidate_reason=classification.reason,
                classifier_signal=classification.signal,
                suggested_decision=classification.suggested_decision,
                confidence=classification.confidence,
                processing_state=CandidateState.pending_review,
            )
        )

    db.commit()


def list_candidates(db: Session, *, include_processed: bool = False) -> list[Candidate]:
    ensure_demo_candidates(db)

    statement = select(Candidate).order_by(Candidate.id.asc())
    if not include_processed:
        statement = statement.where(
            Candidate.processing_state == CandidateState.pending_review
        )

    return list(db.scalars(statement).all())


def list_decisions(db: Session) -> list[Decision]:
    ensure_demo_candidates(db)

    statement = (
        select(Decision)
        .options(selectinload(Decision.candidate))
        .order_by(Decision.created_at.desc(), Decision.id.desc())
    )
    return list(db.scalars(statement).all())


def record_decision(db: Session, payload: DecisionCreate) -> Decision:
    ensure_demo_candidates(db)

    if not payload.confirmed:
        raise HumanApprovalRequiredError(
            "Explicit human confirmation is required before a decision is recorded."
        )

    candidate = db.get(Candidate, payload.candidate_id)
    if candidate is None:
        raise CandidateNotFoundError(f"Candidate {payload.candidate_id} was not found.")

    decision = Decision(
        candidate_id=candidate.id,
        decision=payload.decision,
        note=payload.note,
        human_confirmed=True,
        external_action_status=action_executor.build_external_action_status(
            payload.decision
        ),
    )
    candidate.processing_state = _candidate_state_for_decision(payload.decision)

    db.add(decision)
    db.commit()

    statement = (
        select(Decision)
        .options(selectinload(Decision.candidate))
        .where(Decision.id == decision.id)
    )
    created_decision = db.scalar(statement)
    if created_decision is None:
        raise CandidateNotFoundError(
            "Decision could not be reloaded after persistence."
        )
    return created_decision


def _candidate_state_for_decision(decision: DecisionValue) -> CandidateState:
    if decision == DecisionValue.keep_for_now:
        return CandidateState.kept
    if decision == DecisionValue.mark_low_value:
        return CandidateState.marked_low_value
    return CandidateState.action_recommended
