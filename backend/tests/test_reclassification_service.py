from datetime import datetime, timedelta, timezone
import json

import pytest
from sqlalchemy import func, select

from app.core.security import encrypt_credential
from app.models.candidate import Candidate
from app.models.decision import Decision
from app.models.email_account import EmailAccount
from app.models.enums import (
    CandidateSignal,
    CandidateState,
    ConnectionStatus,
    DecisionValue,
    EmailAccountProvider,
    ExternalActionStatus,
    IngestionStatus,
    IngestionTriggerType,
)
from app.models.ingestion_run import IngestionRun
from app.models.user import User
from app.models.user_email import UserEmail
from app.services.workflow import (
    EmailAccountNotFoundError,
    backfill_source_evidence_for_account,
    reclassify_sources_for_account,
)


def _make_user(db_session, *, email: str, display_name: str) -> User:
    user = User(
        email=email,
        display_name=display_name,
        is_local_alpha=False,
    )
    db_session.add(user)
    db_session.flush()
    db_session.add(
        UserEmail(
            user_id=user.id,
            email=email,
            role="primary",
            is_primary=True,
            is_verified=True,
        )
    )
    db_session.commit()
    db_session.refresh(user)
    return user


def _make_connected_gmail_account(
    db_session,
    *,
    user_id: int,
    account_email: str,
) -> EmailAccount:
    bundle = {
        "access_token": "access-token",
        "refresh_token": "refresh-token",
        "scope": "https://www.googleapis.com/auth/gmail.readonly",
        "token_type": "Bearer",
    }
    account = EmailAccount(
        user_id=user_id,
        provider=EmailAccountProvider.gmail,
        account_email=account_email,
        display_name=account_email,
        connection_status=ConnectionStatus.connected,
        credential_json=encrypt_credential(json.dumps(bundle)),
        token_expiry=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    db_session.add(account)
    db_session.commit()
    db_session.refresh(account)
    return account


def test_reclassify_sources_for_account_updates_classifier_fields_only(
    db_session,
) -> None:
    user = _make_user(
        db_session,
        email="reclassify-user@example.com",
        display_name="Reclassify User",
    )
    other_user = _make_user(
        db_session,
        email="other-user@example.com",
        display_name="Other User",
    )
    account = _make_connected_gmail_account(
        db_session,
        user_id=user.id,
        account_email="alpha.mailbox@example.com",
    )
    other_account = _make_connected_gmail_account(
        db_session,
        user_id=other_user.id,
        account_email="other.mailbox@example.com",
    )

    preserved_credentials = account.credential_json
    preserved_expiry = account.token_expiry

    primary_promotional = Candidate(
        email_account_id=account.id,
        source_key="offers@example.com",
        source_name="Daily Deals Dispatch",
        sender_emails=["offers@dailydeals.example"],
        email_count=12,
        representative_subject="Weekend flash sale and member-only discount roundup",
        mailbox_category="Promotions",
        candidate_reason="Repeated promotional language suggests this source is mostly marketing noise.",
        classifier_signal=CandidateSignal.promotional_digest,
        suggested_decision=DecisionValue.mark_low_value,
        confidence=0.93,
        processing_state=CandidateState.action_recommended,
    )
    primary_ambiguous = Candidate(
        email_account_id=account.id,
        source_key="alerts@cloudbilling.example",
        source_name="Cloud Billing Notices",
        sender_emails=["alerts@cloudbilling.example"],
        email_count=4,
        representative_subject="Usage threshold reminder and invoice preview",
        mailbox_category="Updates",
        candidate_reason="Repeated promotional language suggests this source is mostly marketing noise.",
        classifier_signal=CandidateSignal.promotional_digest,
        suggested_decision=DecisionValue.mark_low_value,
        confidence=0.93,
        processing_state=CandidateState.pending_review,
    )
    untouched_other = Candidate(
        email_account_id=other_account.id,
        source_key="other@example.com",
        source_name="Other Vendor",
        sender_emails=["offers@othervendor.example"],
        email_count=3,
        representative_subject="Limited time offer for other mailbox",
        mailbox_category="Promotions",
        candidate_reason="Repeated promotional language suggests this source is mostly marketing noise.",
        classifier_signal=CandidateSignal.promotional_digest,
        suggested_decision=DecisionValue.mark_low_value,
        confidence=0.93,
        processing_state=CandidateState.pending_review,
    )
    db_session.add_all([primary_promotional, primary_ambiguous, untouched_other])
    db_session.commit()
    db_session.refresh(primary_promotional)

    db_session.add(
        Decision(
            user_id=user.id,
            candidate_id=primary_promotional.id,
            revised_from_decision_id=None,
            decision=DecisionValue.unsubscribe_later,
            note="Preserve this decision history entry.",
            human_confirmed=True,
            external_action_status=ExternalActionStatus.not_executed,
        )
    )
    db_session.add(
        IngestionRun(
            user_id=user.id,
            email_account_id=account.id,
            trigger_type=IngestionTriggerType.manual,
            status=IngestionStatus.completed,
            scope="CATEGORY_PROMOTIONS",
            limit_count=50,
            lookback_days=30,
        )
    )
    db_session.commit()

    summary = reclassify_sources_for_account(db_session, email_account_id=account.id)

    db_session.expire_all()
    refreshed_account = db_session.get(EmailAccount, account.id)
    refreshed_promotional = db_session.get(Candidate, primary_promotional.id)
    refreshed_ambiguous = db_session.get(Candidate, primary_ambiguous.id)
    untouched_other_refreshed = db_session.get(Candidate, untouched_other.id)
    decision_count = db_session.scalar(
        select(func.count())
        .select_from(Decision)
        .where(Decision.candidate_id == primary_promotional.id)
    )
    run_count = db_session.scalar(
        select(func.count())
        .select_from(IngestionRun)
        .where(IngestionRun.email_account_id == account.id)
    )

    assert summary.as_dict() == {
        "account_id": account.id,
        "account_email": "alpha.mailbox@example.com",
        "rows_inspected": 2,
        "rows_changed": 2,
        "resulting_signal_counts": {
            "promotional_digest": 1,
            "recurring_updates": 0,
            "ambiguous_source": 1,
        },
    }
    assert refreshed_account is not None
    assert refreshed_account.connection_status == ConnectionStatus.connected
    assert refreshed_account.credential_json == preserved_credentials
    assert refreshed_account.token_expiry == preserved_expiry
    assert refreshed_promotional is not None
    assert refreshed_promotional.processing_state == CandidateState.action_recommended
    assert refreshed_promotional.classifier_signal == CandidateSignal.promotional_digest
    assert refreshed_promotional.suggested_decision == DecisionValue.mark_low_value
    assert refreshed_promotional.candidate_reason == (
        "Observed promotional cues in stored metadata: 'sale', 'discount', and 'member only'. "
        "Suggest marking this source as low value, while keeping the final decision human-reviewed."
    )
    assert refreshed_promotional.confidence == 0.84
    assert refreshed_ambiguous is not None
    assert refreshed_ambiguous.processing_state == CandidateState.pending_review
    assert refreshed_ambiguous.classifier_signal == CandidateSignal.ambiguous_source
    assert refreshed_ambiguous.suggested_decision == DecisionValue.keep_for_now
    assert refreshed_ambiguous.candidate_reason == (
        "Observed cautionary metadata that can indicate transactional or account-related email: "
        "'invoice', 'billing', and 'usage threshold'. Keep Source for now and review it locally before taking any stronger action."
    )
    assert refreshed_ambiguous.confidence == 0.46
    assert untouched_other_refreshed is not None
    assert untouched_other_refreshed.candidate_reason == (
        "Repeated promotional language suggests this source is mostly marketing noise."
    )
    assert decision_count == 1
    assert run_count == 1


def test_reclassify_sources_for_account_rejects_unknown_mailbox(db_session) -> None:
    with pytest.raises(EmailAccountNotFoundError):
        reclassify_sources_for_account(db_session, email_account_id=999999)


def test_backfill_source_evidence_for_account_updates_sender_domain_only(
    db_session,
) -> None:
    user = _make_user(
        db_session,
        email="backfill-user@example.com",
        display_name="Backfill User",
    )
    other_user = _make_user(
        db_session,
        email="backfill-other@example.com",
        display_name="Backfill Other User",
    )
    account = _make_connected_gmail_account(
        db_session,
        user_id=user.id,
        account_email="backfill.mailbox@example.com",
    )
    other_account = _make_connected_gmail_account(
        db_session,
        user_id=other_user.id,
        account_email="other.backfill@example.com",
    )

    missing_domain = Candidate(
        email_account_id=account.id,
        source_key="offers@dailydeals.example",
        source_name="Daily Deals Dispatch",
        sender_emails=["offers@dailydeals.example"],
        sender_domain=None,
        email_count=12,
        representative_subject="Weekend flash sale and member-only discount roundup",
        representative_message_id=None,
        representative_message_timestamp=None,
        representative_label_ids=None,
        representative_list_id=None,
        has_list_unsubscribe=None,
        mailbox_category="Promotions",
        candidate_reason="Observed promotional cues in stored metadata.",
        classifier_signal=CandidateSignal.promotional_digest,
        suggested_decision=DecisionValue.mark_low_value,
        confidence=0.84,
        processing_state=CandidateState.pending_review,
    )
    already_backfilled = Candidate(
        email_account_id=account.id,
        source_key="alerts@cloudbilling.example",
        source_name="Cloud Billing Notices",
        sender_emails=["alerts@cloudbilling.example"],
        sender_domain="cloudbilling.example",
        email_count=4,
        representative_subject="Usage threshold reminder and invoice preview",
        representative_message_id=None,
        representative_message_timestamp=None,
        representative_label_ids=None,
        representative_list_id=None,
        has_list_unsubscribe=None,
        mailbox_category="Updates",
        candidate_reason="Observed cautionary metadata in stored metadata.",
        classifier_signal=CandidateSignal.ambiguous_source,
        suggested_decision=DecisionValue.keep_for_now,
        confidence=0.46,
        processing_state=CandidateState.pending_review,
    )
    untouched_other = Candidate(
        email_account_id=other_account.id,
        source_key="digest@other.example",
        source_name="Other Vendor",
        sender_emails=["digest@other.example"],
        sender_domain=None,
        email_count=2,
        representative_subject="Other digest",
        representative_message_id=None,
        representative_message_timestamp=None,
        representative_label_ids=None,
        representative_list_id=None,
        has_list_unsubscribe=None,
        mailbox_category="Promotions",
        candidate_reason="Observed promotional cues in stored metadata.",
        classifier_signal=CandidateSignal.promotional_digest,
        suggested_decision=DecisionValue.mark_low_value,
        confidence=0.84,
        processing_state=CandidateState.pending_review,
    )
    db_session.add_all([missing_domain, already_backfilled, untouched_other])
    db_session.commit()

    summary = backfill_source_evidence_for_account(
        db_session,
        email_account_id=account.id,
    )

    db_session.expire_all()
    refreshed_missing_domain = db_session.get(Candidate, missing_domain.id)
    refreshed_already_backfilled = db_session.get(Candidate, already_backfilled.id)
    refreshed_untouched_other = db_session.get(Candidate, untouched_other.id)

    assert summary.as_dict() == {
        "account_id": account.id,
        "account_email": "backfill.mailbox@example.com",
        "rows_inspected": 2,
        "rows_changed": 1,
        "sender_domain_backfilled": 1,
    }
    assert refreshed_missing_domain is not None
    assert refreshed_missing_domain.sender_domain == "dailydeals.example"
    assert refreshed_missing_domain.representative_message_id is None
    assert refreshed_missing_domain.representative_message_timestamp is None
    assert refreshed_missing_domain.representative_label_ids is None
    assert refreshed_missing_domain.representative_list_id is None
    assert refreshed_missing_domain.has_list_unsubscribe is None
    assert refreshed_already_backfilled is not None
    assert refreshed_already_backfilled.sender_domain == "cloudbilling.example"
    assert refreshed_untouched_other is not None
    assert refreshed_untouched_other.sender_domain is None
