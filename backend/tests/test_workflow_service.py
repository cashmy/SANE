from sqlalchemy import func, select

from app.models import Candidate, Decision, User
from app.models.enums import CandidateSignal, CandidateState, DecisionValue
from app.schemas.workflow import BatchDecisionCreate, DecisionCreate
from app.services import action_executor
from app.services.workflow import (
    HumanApprovalRequiredError,
    ensure_demo_candidates,
    list_decisions,
    list_sources,
    record_batch_decision,
    record_decision,
)


def test_source_listing_returns_source_rows_with_email_counts(db_session) -> None:
    result = list_sources(db_session, page=1, page_size=8)
    owner = db_session.scalar(select(User).where(User.is_local_alpha.is_(True)))

    assert result.pagination.total_items == 8
    assert len(result.items) == 8
    assert owner is not None
    assert all(
        source.processing_state == CandidateState.pending_review
        for source in result.items
    )
    assert all(source.user_id == owner.id for source in result.items)
    assert any(
        source.classifier_signal == CandidateSignal.ambiguous_source
        for source in result.items
    )
    assert any(len(source.sender_emails) > 1 for source in result.items)
    assert any(source.email_count >= 40 for source in result.items)
    assert list_decisions(db_session) == []


def test_record_decision_requires_explicit_human_confirmation(db_session) -> None:
    ensure_demo_candidates(db_session)
    candidate = db_session.scalar(select(Candidate).order_by(Candidate.id.asc()))
    assert candidate is not None

    try:
        record_decision(
            db_session,
            DecisionCreate(
                source_id=candidate.id,
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

    outcome = record_decision(
        db_session,
        DecisionCreate(
            source_id=candidate.id,
            decision=DecisionValue.unsubscribe_later,
            confirmed=True,
            note="Keep the action deferred until trust is validated.",
        ),
    )

    db_session.expire_all()
    persisted_decision = db_session.scalar(
        select(Decision).where(Decision.id == outcome.decision.id)
    )
    persisted_candidate = db_session.scalar(
        select(Candidate).where(Candidate.id == candidate.id)
    )

    assert persisted_decision is not None
    assert persisted_candidate is not None
    assert outcome.applied is True
    assert persisted_candidate.user_id == persisted_decision.user_id
    assert persisted_candidate.processing_state == CandidateState.action_recommended
    assert persisted_decision.human_confirmed is True
    assert persisted_decision.external_action_status.value == "not_executed"
    assert external_call["called"] is False


def test_repeating_the_same_decision_is_a_noop(db_session) -> None:
    ensure_demo_candidates(db_session)
    candidate = db_session.scalar(select(Candidate).order_by(Candidate.id.asc()))
    assert candidate is not None

    first = record_decision(
        db_session,
        DecisionCreate(
            source_id=candidate.id,
            decision=DecisionValue.keep_for_now,
            confirmed=True,
        ),
    )
    second = record_decision(
        db_session,
        DecisionCreate(
            source_id=candidate.id,
            decision=DecisionValue.keep_for_now,
            confirmed=True,
        ),
    )

    assert first.applied is True
    assert second.applied is False
    assert first.decision.id == second.decision.id
    assert db_session.scalar(select(func.count()).select_from(Decision)) == 1


def test_revision_appends_a_new_history_event(db_session) -> None:
    ensure_demo_candidates(db_session)
    candidate = db_session.scalar(select(Candidate).order_by(Candidate.id.asc()))
    assert candidate is not None

    first = record_decision(
        db_session,
        DecisionCreate(
            source_id=candidate.id,
            decision=DecisionValue.keep_for_now,
            confirmed=True,
        ),
    )
    second = record_decision(
        db_session,
        DecisionCreate(
            source_id=candidate.id,
            decision=DecisionValue.mark_low_value,
            confirmed=True,
        ),
    )

    history = list_decisions(db_session)
    db_session.expire_all()
    persisted_candidate = db_session.get(Candidate, candidate.id)

    assert first.applied is True
    assert second.applied is True
    assert second.decision.revised_from_decision_id == first.decision.id
    assert persisted_candidate is not None
    assert persisted_candidate.processing_state == CandidateState.marked_low_value
    assert len(history) == 2
    assert history[0].is_current is True
    assert history[0].is_revision is True
    assert history[1].is_current is False


def test_batch_decision_requires_confirmation_and_stays_local(
    db_session, monkeypatch
) -> None:
    ensure_demo_candidates(db_session)
    sources = list(
        db_session.scalars(
            select(Candidate).order_by(Candidate.id.asc()).limit(2)
        ).all()
    )
    assert len(sources) == 2

    external_call = {"called": False}

    def fake_execute_external_action(_: DecisionValue) -> None:
        external_call["called"] = True

    monkeypatch.setattr(
        action_executor, "execute_external_action", fake_execute_external_action
    )

    try:
        record_batch_decision(
            db_session,
            BatchDecisionCreate(
                source_ids=[source.id for source in sources],
                decision=DecisionValue.mark_low_value,
                confirmed=False,
            ),
        )
    except HumanApprovalRequiredError:
        pass
    else:
        raise AssertionError(
            "Batch decisions should require explicit human confirmation."
        )

    result = record_batch_decision(
        db_session,
        BatchDecisionCreate(
            source_ids=[source.id for source in sources],
            decision=DecisionValue.mark_low_value,
            confirmed=True,
            note="Apply the same local low-value decision to the selected sources.",
        ),
    )

    assert len(result.applied) == 2
    assert result.unchanged == []
    assert db_session.scalar(select(func.count()).select_from(Decision)) == 2
    assert all(
        decision.external_action_status.value == "not_executed"
        for decision in result.applied
    )
    assert external_call["called"] is False
