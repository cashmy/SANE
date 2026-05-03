from datetime import datetime, timedelta, timezone
import json

from sqlalchemy import func, select

from app.core.security import encrypt_credential
from app.models.candidate import Candidate
from app.models.decision import Decision
from app.models.email_account import EmailAccount
from app.models.enums import ConnectionStatus, DecisionValue, EmailAccountProvider
from app.models.ingestion_run import IngestionRun
from app.models.user import User
from app.models.user_email import UserEmail


def _make_connected_gmail_account(db_session, *, user_id: int) -> EmailAccount:
    bundle = {
        "access_token": "access-token",
        "refresh_token": "refresh-token",
        "scope": "https://www.googleapis.com/auth/gmail.readonly",
        "token_type": "Bearer",
    }
    account = EmailAccount(
        user_id=user_id,
        provider=EmailAccountProvider.gmail,
        account_email="person@gmail.com",
        display_name="person@gmail.com",
        connection_status=ConnectionStatus.connected,
        credential_json=encrypt_credential(json.dumps(bundle)),
        token_expiry=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    db_session.add(account)
    db_session.commit()
    db_session.refresh(account)
    return account


def test_gmail_accounts_unauthenticated_returns_401(client) -> None:
    response = client.get("/api/gmail/accounts")

    assert response.status_code == 401


def test_gmail_accounts_empty_for_local_alpha(auth_client) -> None:
    response = auth_client.get("/api/gmail/accounts")

    assert response.status_code == 200
    assert response.json() == []


def test_reset_local_data_unauthenticated_returns_401(client) -> None:
    response = client.post(
        "/api/gmail/accounts/1/reset-local-data",
        json={"mode": "sources_and_decisions", "confirmed": True},
    )

    assert response.status_code == 401


def test_scan_unauthenticated_returns_401(client) -> None:
    response = client.post(
        "/api/gmail/scan",
        json={"email_account_id": 1, "limit_count": 50, "scope": "CATEGORY_PROMOTIONS"},
    )

    assert response.status_code == 401


def test_scan_nonexistent_account_returns_404(authenticated_client_factory) -> None:
    client, _user = authenticated_client_factory()

    response = client.post(
        "/api/gmail/scan",
        json={
            "email_account_id": 999,
            "limit_count": 50,
            "scope": "CATEGORY_PROMOTIONS",
        },
    )

    assert response.status_code == 404


def test_scan_disconnected_account_returns_409(
    authenticated_client_factory,
    db_session,
) -> None:
    client, user = authenticated_client_factory()
    account = EmailAccount(
        user_id=user.id,
        provider=EmailAccountProvider.gmail,
        account_email="person@gmail.com",
        display_name="person@gmail.com",
        connection_status=ConnectionStatus.disconnected,
    )
    db_session.add(account)
    db_session.commit()

    response = client.post(
        "/api/gmail/scan",
        json={
            "email_account_id": account.id,
            "limit_count": 50,
            "scope": "CATEGORY_PROMOTIONS",
        },
    )

    assert response.status_code == 409


def test_scan_creates_ingestion_run_and_candidates(
    authenticated_client_factory,
    db_session,
    monkeypatch,
) -> None:
    client, user = authenticated_client_factory()
    account = _make_connected_gmail_account(db_session, user_id=user.id)

    monkeypatch.setattr(
        "app.services.gmail_service._list_message_ids",
        lambda _token, _limit, _scope: ["m1", "m2", "m3"],
    )

    def fake_metadata(_token: str, message_id: str) -> dict:
        if message_id in {"m1", "m2"}:
            from_value = "Deals Team <offers@example.com>"
            subject = "Weekend sale alert"
        else:
            from_value = "Digest Team <digest@example.com>"
            subject = "Weekly roundup"

        return {
            "id": message_id,
            "internalDate": "1714740000000" if message_id == "m1" else "1714743600000",
            "labelIds": ["CATEGORY_PROMOTIONS"],
            "snippet": subject,
            "payload": {
                "headers": [
                    {"name": "From", "value": from_value},
                    {"name": "Subject", "value": subject},
                ]
            },
        }

    monkeypatch.setattr(
        "app.services.gmail_service._get_message_metadata", fake_metadata
    )

    response = client.post(
        "/api/gmail/scan",
        json={
            "email_account_id": account.id,
            "limit_count": 50,
            "scope": "CATEGORY_PROMOTIONS",
        },
    )

    db_session.expire_all()
    candidate_count = db_session.scalar(
        select(func.count())
        .select_from(Candidate)
        .where(Candidate.email_account_id == account.id)
    )
    run_count = db_session.scalar(
        select(func.count())
        .select_from(IngestionRun)
        .where(IngestionRun.email_account_id == account.id)
    )
    counts = {
        row.source_key: row.email_count
        for row in db_session.scalars(
            select(Candidate).where(Candidate.email_account_id == account.id)
        ).all()
    }

    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert response.json()["message_count_scanned"] == 3
    assert response.json()["source_count_seen"] == 2
    assert response.json()["source_count_created"] == 2
    assert candidate_count == 2
    assert run_count == 1
    assert counts["offers@example.com"] == 2
    assert counts["digest@example.com"] == 1


def test_scan_respects_limit_count(
    authenticated_client_factory,
    db_session,
    monkeypatch,
) -> None:
    client, user = authenticated_client_factory(email="limit-user@example.com")
    account = _make_connected_gmail_account(db_session, user_id=user.id)
    observed: dict[str, int] = {}

    def fake_list(_token: str, limit_count: int, _scope: str) -> list[str]:
        observed["limit"] = limit_count
        return []

    monkeypatch.setattr("app.services.gmail_service._list_message_ids", fake_list)

    response = client.post(
        "/api/gmail/scan",
        json={
            "email_account_id": account.id,
            "limit_count": 100,
            "scope": "CATEGORY_PROMOTIONS",
        },
    )

    assert response.status_code == 200
    assert observed["limit"] == 100
    assert response.json()["limit_count"] == 100


def test_scan_does_not_duplicate_existing_candidates(
    authenticated_client_factory,
    db_session,
    monkeypatch,
) -> None:
    client, user = authenticated_client_factory(email="repeat-user@example.com")
    account = _make_connected_gmail_account(db_session, user_id=user.id)

    monkeypatch.setattr(
        "app.services.gmail_service._list_message_ids",
        lambda _token, _limit, _scope: ["m1"],
    )
    monkeypatch.setattr(
        "app.services.gmail_service._get_message_metadata",
        lambda _token, _message_id: {
            "id": "m1",
            "labelIds": ["CATEGORY_PROMOTIONS"],
            "snippet": "Weekend sale alert",
            "payload": {
                "headers": [
                    {"name": "From", "value": "Deals Team <offers@example.com>"},
                    {"name": "Subject", "value": "Weekend sale alert"},
                ]
            },
        },
    )

    first = client.post(
        "/api/gmail/scan",
        json={
            "email_account_id": account.id,
            "limit_count": 50,
            "scope": "CATEGORY_PROMOTIONS",
        },
    )
    second = client.post(
        "/api/gmail/scan",
        json={
            "email_account_id": account.id,
            "limit_count": 50,
            "scope": "CATEGORY_PROMOTIONS",
        },
    )

    db_session.expire_all()
    candidate_count = db_session.scalar(
        select(func.count())
        .select_from(Candidate)
        .where(Candidate.email_account_id == account.id)
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["source_count_seen"] == 1
    assert second.json()["source_count_created"] == 0
    assert candidate_count == 1


def test_scan_uses_sender_domain_fallback_and_latest_subject_for_representative_row(
    authenticated_client_factory,
    db_session,
    monkeypatch,
) -> None:
    client, user = authenticated_client_factory(email="normalize-user@example.com")
    account = _make_connected_gmail_account(db_session, user_id=user.id)

    monkeypatch.setattr(
        "app.services.gmail_service._list_message_ids",
        lambda _token, _limit, _scope: ["m1", "m2"],
    )

    def fake_metadata(_token: str, message_id: str) -> dict:
        if message_id == "m1":
            return {
                "id": message_id,
                "internalDate": "1714740000000",
                "labelIds": ["CATEGORY_PROMOTIONS"],
                "snippet": "Older promotional snippet",
                "payload": {
                    "headers": [
                        {"name": "From", "value": "offers@example.com"},
                        {"name": "Subject", "value": "Older subject"},
                    ]
                },
            }

        return {
            "id": message_id,
            "internalDate": "1714743600000",
            "labelIds": ["CATEGORY_PROMOTIONS"],
            "snippet": "Latest promotional snippet",
            "payload": {
                "headers": [
                    {"name": "From", "value": "offers@example.com"},
                    {"name": "Subject", "value": "Latest subject"},
                ]
            },
        }

    monkeypatch.setattr(
        "app.services.gmail_service._get_message_metadata", fake_metadata
    )

    response = client.post(
        "/api/gmail/scan",
        json={
            "email_account_id": account.id,
            "limit_count": 50,
            "scope": "CATEGORY_PROMOTIONS",
        },
    )

    candidate = db_session.scalar(
        select(Candidate).where(Candidate.email_account_id == account.id)
    )

    assert response.status_code == 200
    assert candidate is not None
    assert candidate.source_name == "example.com"
    assert candidate.email_count == 2
    assert candidate.representative_subject == "Latest subject"


def test_scan_does_not_collapse_same_domain_marketing_and_transactional_senders(
    authenticated_client_factory,
    db_session,
    monkeypatch,
) -> None:
    client, user = authenticated_client_factory(email="safety-user@example.com")
    account = _make_connected_gmail_account(db_session, user_id=user.id)

    monkeypatch.setattr(
        "app.services.gmail_service._list_message_ids",
        lambda _token, _limit, _scope: ["m1", "m2"],
    )

    def fake_metadata(_token: str, message_id: str) -> dict:
        if message_id == "m1":
            return {
                "id": message_id,
                "internalDate": "1714740000000",
                "labelIds": ["CATEGORY_PROMOTIONS"],
                "snippet": "Weekend sale",
                "payload": {
                    "headers": [
                        {"name": "From", "value": "Brand Deals <offers@brand.example>"},
                        {"name": "Subject", "value": "Weekend sale"},
                    ]
                },
            }

        return {
            "id": message_id,
            "internalDate": "1714743600000",
            "labelIds": ["CATEGORY_PROMOTIONS"],
            "snippet": "Security alert",
            "payload": {
                "headers": [
                    {"name": "From", "value": "Brand Security <alerts@brand.example>"},
                    {"name": "Subject", "value": "Security alert"},
                ]
            },
        }

    monkeypatch.setattr(
        "app.services.gmail_service._get_message_metadata", fake_metadata
    )

    response = client.post(
        "/api/gmail/scan",
        json={
            "email_account_id": account.id,
            "limit_count": 50,
            "scope": "CATEGORY_PROMOTIONS",
        },
    )

    candidates = list(
        db_session.scalars(
            select(Candidate)
            .where(Candidate.email_account_id == account.id)
            .order_by(Candidate.source_key.asc())
        ).all()
    )

    assert response.status_code == 200
    assert [candidate.source_key for candidate in candidates] == [
        "alerts@brand.example",
        "offers@brand.example",
    ]


def test_repeat_scan_preserves_existing_decision_history(
    authenticated_client_factory,
    db_session,
    monkeypatch,
) -> None:
    client, user = authenticated_client_factory(email="decision-user@example.com")
    account = _make_connected_gmail_account(db_session, user_id=user.id)

    monkeypatch.setattr(
        "app.services.gmail_service._list_message_ids",
        lambda _token, _limit, _scope: ["m1"],
    )
    monkeypatch.setattr(
        "app.services.gmail_service._get_message_metadata",
        lambda _token, _message_id: {
            "id": "m1",
            "internalDate": "1714740000000",
            "labelIds": ["CATEGORY_PROMOTIONS"],
            "snippet": "Weekend sale alert",
            "payload": {
                "headers": [
                    {"name": "From", "value": "Deals Team <offers@example.com>"},
                    {"name": "Subject", "value": "Weekend sale alert"},
                ]
            },
        },
    )

    first = client.post(
        "/api/gmail/scan",
        json={
            "email_account_id": account.id,
            "limit_count": 50,
            "scope": "CATEGORY_PROMOTIONS",
        },
    )

    candidate = db_session.scalar(
        select(Candidate).where(Candidate.email_account_id == account.id)
    )
    assert candidate is not None
    db_session.add(
        Decision(
            user_id=user.id,
            candidate_id=candidate.id,
            decision=DecisionValue.keep_for_now,
            human_confirmed=True,
            external_action_status="not_executed",
        )
    )
    db_session.commit()

    second = client.post(
        "/api/gmail/scan",
        json={
            "email_account_id": account.id,
            "limit_count": 50,
            "scope": "CATEGORY_PROMOTIONS",
        },
    )

    db_session.expire_all()
    refreshed_candidate = db_session.get(Candidate, candidate.id)
    decision_count = db_session.scalar(
        select(func.count())
        .select_from(Decision)
        .where(Decision.candidate_id == candidate.id)
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["source_count_created"] == 0
    assert second.json()["source_count_seen"] == 1
    assert refreshed_candidate is not None
    assert refreshed_candidate.current_decision == DecisionValue.keep_for_now
    assert decision_count == 1


def test_disconnect_clears_credentials_and_marks_disconnected(
    authenticated_client_factory,
    db_session,
) -> None:
    client, user = authenticated_client_factory(email="disconnect-user@example.com")
    account = _make_connected_gmail_account(db_session, user_id=user.id)

    response = client.post(
        "/api/gmail/disconnect",
        json={"email_account_id": account.id},
    )

    db_session.expire_all()
    refreshed = db_session.get(EmailAccount, account.id)

    assert response.status_code == 204
    assert refreshed is not None
    assert refreshed.credential_json is None
    assert refreshed.token_expiry is None
    assert refreshed.connection_status == ConnectionStatus.disconnected


def test_disconnect_preserves_existing_candidates(
    authenticated_client_factory,
    db_session,
) -> None:
    client, user = authenticated_client_factory(email="preserve-user@example.com")
    account = _make_connected_gmail_account(db_session, user_id=user.id)
    db_session.add(
        Candidate(
            email_account_id=account.id,
            source_key="offers@example.com",
            source_name="Deals Team",
            sender_emails=["offers@example.com"],
            email_count=1,
            representative_subject="Weekend sale alert",
            mailbox_category="Promotions",
            candidate_reason="Promo",
            classifier_signal="promotional_digest",
            suggested_decision="mark_low_value",
            confidence=0.9,
        )
    )
    db_session.commit()

    response = client.post(
        "/api/gmail/disconnect",
        json={"email_account_id": account.id},
    )

    remaining = db_session.scalar(
        select(func.count())
        .select_from(Candidate)
        .where(Candidate.email_account_id == account.id)
    )

    assert response.status_code == 204
    assert remaining == 1


def test_reset_local_data_requires_confirmation(
    authenticated_client_factory,
    db_session,
) -> None:
    client, user = authenticated_client_factory(email="reset-confirm@example.com")
    account = _make_connected_gmail_account(db_session, user_id=user.id)

    response = client.post(
        f"/api/gmail/accounts/{account.id}/reset-local-data",
        json={"mode": "sources_and_decisions", "confirmed": False},
    )

    assert response.status_code == 400
    assert "human confirmation" in response.json()["detail"].lower()


def test_reset_local_data_rejects_sources_only_mode(
    authenticated_client_factory,
    db_session,
) -> None:
    client, user = authenticated_client_factory(email="reset-sources-only@example.com")
    account = _make_connected_gmail_account(db_session, user_id=user.id)

    response = client.post(
        f"/api/gmail/accounts/{account.id}/reset-local-data",
        json={"mode": "sources_only", "confirmed": True},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Current ALPHA data model cannot preserve decisions when sources are deleted."
    )


def test_reset_local_data_rejects_accounts_owned_by_another_user(
    authenticated_client_factory,
    db_session,
) -> None:
    client, _user = authenticated_client_factory(email="reset-owner-a@example.com")
    other_user = User(
        email="reset-owner-b@example.com",
        display_name="Reset Owner B",
        is_local_alpha=False,
    )
    db_session.add(other_user)
    db_session.flush()
    db_session.add(
        UserEmail(
            user_id=other_user.id,
            email="reset-owner-b@example.com",
            role="primary",
            is_primary=True,
            is_verified=True,
        )
    )
    db_session.commit()
    account = _make_connected_gmail_account(db_session, user_id=other_user.id)

    response = client.post(
        f"/api/gmail/accounts/{account.id}/reset-local-data",
        json={"mode": "sources_and_decisions", "confirmed": True},
    )

    assert response.status_code == 404


def test_reset_local_data_deletes_selected_account_sources_and_decisions_only(
    authenticated_client_factory,
    db_session,
) -> None:
    client, user = authenticated_client_factory(email="reset-delete@example.com")
    account = _make_connected_gmail_account(db_session, user_id=user.id)
    other_account = EmailAccount(
        user_id=user.id,
        provider=EmailAccountProvider.gmail,
        account_email="other@gmail.com",
        display_name="other@gmail.com",
        connection_status=ConnectionStatus.connected,
        credential_json=account.credential_json,
        token_expiry=account.token_expiry,
    )
    db_session.add(other_account)
    db_session.commit()
    db_session.refresh(other_account)

    primary_candidate = Candidate(
        email_account_id=account.id,
        source_key="offers@example.com",
        source_name="Deals Team",
        sender_emails=["offers@example.com"],
        email_count=1,
        representative_subject="Weekend sale alert",
        mailbox_category="Promotions",
        candidate_reason="Promo",
        classifier_signal="promotional_digest",
        suggested_decision="mark_low_value",
        confidence=0.9,
    )
    other_candidate = Candidate(
        email_account_id=other_account.id,
        source_key="digest@example.com",
        source_name="Digest Team",
        sender_emails=["digest@example.com"],
        email_count=1,
        representative_subject="Weekly digest",
        mailbox_category="Promotions",
        candidate_reason="Promo",
        classifier_signal="promotional_digest",
        suggested_decision="mark_low_value",
        confidence=0.9,
    )
    run = IngestionRun(
        user_id=user.id,
        email_account_id=account.id,
        trigger_type="manual",
        status="completed",
        scope="CATEGORY_PROMOTIONS",
        limit_count=50,
        message_count_scanned=10,
        source_count_seen=1,
        source_count_created=1,
    )
    db_session.add_all([primary_candidate, other_candidate, run])
    db_session.commit()
    db_session.refresh(primary_candidate)
    db_session.refresh(other_candidate)

    db_session.add_all(
        [
            Decision(
                user_id=user.id,
                candidate_id=primary_candidate.id,
                decision=DecisionValue.keep_for_now,
                human_confirmed=True,
                external_action_status="not_executed",
            ),
            Decision(
                user_id=user.id,
                candidate_id=other_candidate.id,
                decision=DecisionValue.mark_low_value,
                human_confirmed=True,
                external_action_status="not_executed",
            ),
        ]
    )
    db_session.commit()

    original_credentials = account.credential_json
    original_expiry = account.token_expiry

    response = client.post(
        f"/api/gmail/accounts/{account.id}/reset-local-data",
        json={"mode": "sources_and_decisions", "confirmed": True},
    )

    db_session.expire_all()
    refreshed_account = db_session.get(EmailAccount, account.id)
    remaining_primary_sources = db_session.scalar(
        select(func.count())
        .select_from(Candidate)
        .where(Candidate.email_account_id == account.id)
    )
    remaining_other_sources = db_session.scalar(
        select(func.count())
        .select_from(Candidate)
        .where(Candidate.email_account_id == other_account.id)
    )
    remaining_primary_decisions = db_session.scalar(
        select(func.count())
        .select_from(Decision)
        .join(Candidate, Decision.candidate_id == Candidate.id)
        .where(Candidate.email_account_id == account.id)
    )
    remaining_other_decisions = db_session.scalar(
        select(func.count())
        .select_from(Decision)
        .join(Candidate, Decision.candidate_id == Candidate.id)
        .where(Candidate.email_account_id == other_account.id)
    )
    remaining_runs = db_session.scalar(
        select(func.count())
        .select_from(IngestionRun)
        .where(IngestionRun.email_account_id == account.id)
    )

    assert response.status_code == 200
    assert response.json() == {
        "account_id": account.id,
        "account_email": "person@gmail.com",
        "mode": "sources_and_decisions",
        "sources_deleted": 1,
        "decisions_deleted": 1,
        "ingestion_runs_preserved": 1,
        "ingestion_runs_deleted": 0,
    }
    assert refreshed_account is not None
    assert refreshed_account.connection_status == ConnectionStatus.connected
    assert refreshed_account.credential_json == original_credentials
    assert refreshed_account.token_expiry == original_expiry
    assert remaining_primary_sources == 0
    assert remaining_primary_decisions == 0
    assert remaining_other_sources == 1
    assert remaining_other_decisions == 1
    assert remaining_runs == 1


def test_reset_local_data_allows_fresh_scan_after_reset(
    authenticated_client_factory,
    db_session,
    monkeypatch,
) -> None:
    client, user = authenticated_client_factory(email="reset-rescan@example.com")
    account = _make_connected_gmail_account(db_session, user_id=user.id)
    db_session.add(
        Candidate(
            email_account_id=account.id,
            source_key="offers@example.com",
            source_name="Deals Team",
            sender_emails=["offers@example.com"],
            email_count=1,
            representative_subject="Weekend sale alert",
            mailbox_category="Promotions",
            candidate_reason="Promo",
            classifier_signal="promotional_digest",
            suggested_decision="mark_low_value",
            confidence=0.9,
        )
    )
    db_session.commit()

    reset_response = client.post(
        f"/api/gmail/accounts/{account.id}/reset-local-data",
        json={"mode": "sources_and_decisions", "confirmed": True},
    )

    monkeypatch.setattr(
        "app.services.gmail_service._list_message_ids",
        lambda _token, _limit, _scope: ["m1"],
    )
    monkeypatch.setattr(
        "app.services.gmail_service._get_message_metadata",
        lambda _token, _message_id: {
            "id": "m1",
            "internalDate": "1714740000000",
            "labelIds": ["CATEGORY_PROMOTIONS"],
            "snippet": "Weekend sale alert",
            "payload": {
                "headers": [
                    {"name": "From", "value": "Deals Team <offers@example.com>"},
                    {"name": "Subject", "value": "Weekend sale alert"},
                ]
            },
        },
    )

    scan_response = client.post(
        "/api/gmail/scan",
        json={
            "email_account_id": account.id,
            "limit_count": 50,
            "scope": "CATEGORY_PROMOTIONS",
        },
    )

    source_count = db_session.scalar(
        select(func.count())
        .select_from(Candidate)
        .where(Candidate.email_account_id == account.id)
    )
    run_count = db_session.scalar(
        select(func.count())
        .select_from(IngestionRun)
        .where(IngestionRun.email_account_id == account.id)
    )

    assert reset_response.status_code == 200
    assert scan_response.status_code == 200
    assert scan_response.json()["source_count_created"] == 1
    assert source_count == 1
    assert run_count == 1


def test_list_runs_unauthenticated_returns_401(client) -> None:
    response = client.get("/api/gmail/runs/1")

    assert response.status_code == 401


def test_list_runs_returns_empty_list_before_any_scan(
    authenticated_client_factory,
    db_session,
) -> None:
    client, user = authenticated_client_factory(email="runs-user@example.com")
    account = _make_connected_gmail_account(db_session, user_id=user.id)

    response = client.get(f"/api/gmail/runs/{account.id}")

    assert response.status_code == 200
    assert response.json() == []
