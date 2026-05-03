from datetime import datetime, timedelta, timezone
import json

from sqlalchemy import func, select

from app.core.security import encrypt_credential
from app.models.candidate import Candidate
from app.models.email_account import EmailAccount
from app.models.enums import ConnectionStatus, EmailAccountProvider
from app.models.ingestion_run import IngestionRun


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

    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert response.json()["message_count_scanned"] == 3
    assert response.json()["source_count_created"] == 2
    assert candidate_count == 2
    assert run_count == 1


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
    assert second.json()["source_count_created"] == 0
    assert candidate_count == 1


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
