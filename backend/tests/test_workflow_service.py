from sqlalchemy import func, select

from app.models import Candidate, Decision
from app.models.enums import CandidateSignal, CandidateState, DecisionValue
from app.schemas.workflow import DecisionCreate
from app.services import action_executor
from app.services.workflow import (
    HumanApprovalRequiredError,
    ensure_demo_candidates,
    list_decisions,
    record_decision,
)


def test_classifier_suggestion_does_not_become_final_authority(db_session) -> None:
    ensure_demo_candidates(db_session)

    candidates = list(
        db_session.scalars(select(Candidate).order_by(Candidate.id.asc())).all()
    )

    assert candidates
    assert all(
        candidate.processing_state == CandidateState.pending_review
        for candidate in candidates
    )
    assert any(
        candidate.classifier_signal == CandidateSignal.ambiguous_source
        for candidate in candidates
    )
    assert list_decisions(db_session) == []


def test_record_decision_requires_explicit_human_confirmation(db_session) -> None:
    ensure_demo_candidates(db_session)
    candidate = db_session.scalar(select(Candidate).order_by(Candidate.id.asc()))
    assert candidate is not None

    try:
        record_decision(
            db_session,
            DecisionCreate(
                candidate_id=candidate.id,
                decision=DecisionValue.mark_low_value,
                confirmed=False,
            ),
        )
    except HumanApprovalRequiredError:
        pass
    else:
        raise AssertionError(
            "Decision recording should fail without explicit human confirmation."
        )

    assert db_session.scalar(select(func.count()).select_from(Decision)) == 0


def test_record_decision_persists_without_external_execution(
    db_session, monkeypatch
) -> None:
    ensure_demo_candidates(db_session)
    candidate = db_session.scalar(select(Candidate).order_by(Candidate.id.asc()))
    assert candidate is not None

    external_call = {"called": False}

    def fake_execute_external_action(_: DecisionValue) -> None:
        external_call["called"] = True

    monkeypatch.setattr(
        action_executor, "execute_external_action", fake_execute_external_action
    )

    created_decision = record_decision(
        db_session,
        DecisionCreate(
            candidate_id=candidate.id,
            decision=DecisionValue.unsubscribe_later,
            confirmed=True,
            note="Keep the action deferred until trust is validated.",
        ),
    )

    db_session.expire_all()
    persisted_decision = db_session.scalar(
        select(Decision).where(Decision.id == created_decision.id)
    )
    persisted_candidate = db_session.scalar(
        select(Candidate).where(Candidate.id == candidate.id)
    )

    assert persisted_decision is not None
    assert persisted_candidate is not None
    assert persisted_candidate.processing_state == CandidateState.action_recommended
    assert persisted_decision.human_confirmed is True
    assert persisted_decision.external_action_status.value == "not_executed"
    assert external_call["called"] is False
