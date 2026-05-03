from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.models import Candidate, Decision, User
from app.models.email_account import EmailAccount
from app.models.enums import (
    CandidateSignal,
    CandidateState,
    ConnectionStatus,
    DecisionValue,
    EmailAccountProvider,
    IngestionStatus,
    IngestionTriggerType,
)
from app.models.ingestion_run import IngestionRun
from app.schemas.workflow import BatchDecisionCreate, DecisionCreate
from app.services import action_executor
from app.services.ownership import (
    get_or_create_local_alpha_email_account,
    get_or_create_local_alpha_user,
)
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
    account = db_session.scalar(
        select(EmailAccount).where(
            EmailAccount.provider == EmailAccountProvider.local_alpha
        )
    )

    assert result.pagination.total_items == 8
    assert len(result.items) == 8
    assert account is not None
    assert all(
        source.processing_state == CandidateState.pending_review
        for source in result.items
    )
    assert all(source.email_account_id == account.id for source in result.items)
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
    # Controlled denormalization invariant: Decision.user_id must equal the user_id
    # of the EmailAccount that owns the source.  Decision.user_id is kept as a direct
    # FK for query/authorization convenience, not as a strict source-ownership link.
    account = db_session.get(EmailAccount, persisted_candidate.email_account_id)
    assert account is not None
    assert persisted_decision.user_id == account.user_id
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


def test_same_email_account_cannot_have_duplicate_source_keys(db_session) -> None:
    """The unique constraint is now scoped to (email_account_id, source_key)."""
    ensure_demo_candidates(db_session)
    user = get_or_create_local_alpha_user(db_session)
    account = get_or_create_local_alpha_email_account(db_session, user)

    duplicate = Candidate(
        email_account_id=account.id,
        source_key="daily-deals-dispatch",
        source_name="Duplicate Daily Deals Dispatch",
        sender_emails=["duplicate@dailydeals.example"],
        email_count=1,
        representative_subject="Duplicate source should fail for the same email account",
        mailbox_category="Promotions",
        candidate_reason="Duplicate source identity for the same account should be rejected.",
        classifier_signal=CandidateSignal.promotional_digest,
        suggested_decision=DecisionValue.mark_low_value,
        processing_state=CandidateState.pending_review,
    )
    db_session.add(duplicate)

    try:
        db_session.flush()
    except IntegrityError:
        db_session.rollback()
    else:
        raise AssertionError(
            "The same email account should not be able to persist a duplicate source_key."
        )


def test_different_email_accounts_can_share_the_same_source_key(db_session) -> None:
    """Duplicate source_keys are allowed across different email accounts."""
    ensure_demo_candidates(db_session)
    user = get_or_create_local_alpha_user(db_session)
    alpha_account = get_or_create_local_alpha_email_account(db_session, user)

    # A second user with their own email account.
    other_user = User(
        email="second-user@sane.local",
        display_name="Second User",
        is_local_alpha=False,
    )
    db_session.add(other_user)
    db_session.flush()

    other_account = EmailAccount(
        user_id=other_user.id,
        provider=EmailAccountProvider.local_alpha,
        account_email="second-account@sane.local",
        display_name="Second Account",
        connection_status=ConnectionStatus.local_only,
    )
    db_session.add(other_account)
    db_session.flush()

    candidate_for_other_account = Candidate(
        email_account_id=other_account.id,
        source_key="daily-deals-dispatch",
        source_name="Daily Deals Dispatch",
        sender_emails=["offers@dailydeals.example"],
        email_count=11,
        representative_subject="Shared vendor identity should be allowed across accounts",
        mailbox_category="Promotions",
        candidate_reason="Different email accounts may share the same source identity.",
        classifier_signal=CandidateSignal.promotional_digest,
        suggested_decision=DecisionValue.mark_low_value,
        processing_state=CandidateState.pending_review,
    )
    db_session.add(candidate_for_other_account)
    db_session.commit()

    persisted = list(
        db_session.scalars(
            select(Candidate)
            .where(Candidate.source_key == "daily-deals-dispatch")
            .order_by(Candidate.email_account_id.asc())
        ).all()
    )

    assert alpha_account.id != other_account.id
    assert len(persisted) == 2
    assert {c.email_account_id for c in persisted} == {
        alpha_account.id,
        other_account.id,
    }


def test_local_alpha_user_gets_local_alpha_email_account(db_session) -> None:
    """ensure_demo_candidates must provision a local alpha email account."""
    account = ensure_demo_candidates(db_session)
    user = db_session.get(User, account.user_id)

    assert user is not None
    assert user.is_local_alpha is True
    assert account.provider == EmailAccountProvider.local_alpha
    assert account.account_email == "local-alpha@sane.local"
    assert account.connection_status == ConnectionStatus.local_only


def test_demo_sources_belong_to_local_alpha_email_account(db_session) -> None:
    """All seeded demo candidates must be owned by the local ALPHA email account."""
    account = ensure_demo_candidates(db_session)
    candidates = list(
        db_session.scalars(
            select(Candidate).where(Candidate.email_account_id == account.id)
        ).all()
    )

    assert len(candidates) == 8
    assert all(c.email_account_id == account.id for c in candidates)


def test_decision_user_id_matches_source_email_account_user_id(db_session) -> None:
    """Controlled denormalization invariant: Decision.user_id == EmailAccount.user_id.

    Decision.user_id is retained as a direct FK to users for query/authorization
    convenience.  It must always equal the user_id of the EmailAccount that owns
    the source from which the decision was made.
    """
    ensure_demo_candidates(db_session)
    candidate = db_session.scalar(select(Candidate).order_by(Candidate.id.asc()))
    assert candidate is not None

    account = db_session.get(EmailAccount, candidate.email_account_id)
    assert account is not None

    outcome = record_decision(
        db_session,
        DecisionCreate(
            source_id=candidate.id,
            decision=DecisionValue.mark_low_value,
            confirmed=True,
        ),
    )

    db_session.expire_all()
    decision = db_session.get(Decision, outcome.decision.id)
    assert decision is not None
    # Invariant: Decision.user_id == source's EmailAccount.user_id
    assert decision.user_id == account.user_id


def test_ingestion_run_can_be_created_without_executing_gmail(db_session) -> None:
    """IngestionRun model is available for future Gmail work; no scan logic runs here."""
    account = ensure_demo_candidates(db_session)

    run = IngestionRun(
        user_id=account.user_id,
        email_account_id=account.id,
        trigger_type=IngestionTriggerType.alpha_test,
        status=IngestionStatus.pending,
        scope="promotions",
        limit_count=100,
        lookback_days=30,
    )
    db_session.add(run)
    db_session.commit()

    db_session.expire_all()
    persisted = db_session.get(IngestionRun, run.id)
    assert persisted is not None
    assert persisted.status == IngestionStatus.pending
    assert persisted.email_account_id == account.id
    assert persisted.user_id == account.user_id
    assert persisted.message_count_scanned == 0
    assert persisted.source_count_created == 0
