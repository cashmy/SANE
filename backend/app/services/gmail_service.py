from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parseaddr
import json
from typing import Any
from urllib.parse import urlencode

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import decrypt_credential, encrypt_credential
from app.models.candidate import Candidate
from app.models.email_account import EmailAccount
from app.models.enums import (
    ConnectionStatus,
    EmailAccountProvider,
    IngestionStatus,
    IngestionTriggerType,
)
from app.models.ingestion_run import IngestionRun
from app.models.user import User
from app.services.auth_service import OAuthNotConfiguredError
from app.services.classifier import classify_demo_candidate

_GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
_GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
_GMAIL_API_BASE = "https://gmail.googleapis.com/gmail/v1/users/me"
_GMAIL_READONLY_SCOPE = "https://www.googleapis.com/auth/gmail.readonly"
_ALLOWED_LIMIT_VALUES = {50, 100, 200}
_DEFAULT_SCOPE = "CATEGORY_PROMOTIONS"
_SCOPE_LABELS = {"CATEGORY_PROMOTIONS": "Promotions"}


class GmailAccountNotFoundError(LookupError):
    pass


class GmailAccountDisconnectedError(RuntimeError):
    pass


class GmailScanValidationError(ValueError):
    pass


@dataclass
class _NormalizedSource:
    source_key: str
    source_name: str
    sender_email: str
    representative_subject: str
    mailbox_category: str
    message_count: int


def get_gmail_connect_url(state: str) -> str:
    settings = _require_google_oauth_config()
    query = urlencode(
        {
            "client_id": settings.google_client_id,
            "redirect_uri": settings.gmail_redirect_uri,
            "response_type": "code",
            "scope": _GMAIL_READONLY_SCOPE,
            "state": state,
            "access_type": "offline",
            "include_granted_scopes": "true",
            "prompt": "consent",
        }
    )
    return f"{_GOOGLE_AUTH_URL}?{query}"


def exchange_gmail_code(code: str) -> dict[str, Any]:
    settings = _require_google_oauth_config()
    response = httpx.post(
        _GOOGLE_TOKEN_URL,
        data={
            "code": code,
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uri": settings.gmail_redirect_uri,
            "grant_type": "authorization_code",
        },
        timeout=15.0,
    )
    response.raise_for_status()
    return response.json()


def refresh_gmail_access_token(refresh_token: str) -> dict[str, Any]:
    settings = _require_google_oauth_config()
    response = httpx.post(
        _GOOGLE_TOKEN_URL,
        data={
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        },
        timeout=15.0,
    )
    response.raise_for_status()
    return response.json()


def connect_gmail_account(
    db: Session, *, user: User, tokens: dict[str, Any]
) -> EmailAccount:
    access_token = tokens.get("access_token")
    if not access_token:
        raise GmailAccountDisconnectedError(
            "Gmail OAuth response did not include an access token."
        )

    profile = _fetch_gmail_profile(access_token)
    account_email = str(profile.get("emailAddress", "")).strip().lower()
    if not account_email:
        raise GmailAccountDisconnectedError(
            "Gmail profile response did not include an account email."
        )

    account = db.scalar(
        select(EmailAccount).where(
            EmailAccount.user_id == user.id,
            EmailAccount.provider == EmailAccountProvider.gmail,
            EmailAccount.account_email == account_email,
        )
    )
    if account is None:
        account = EmailAccount(
            user_id=user.id,
            provider=EmailAccountProvider.gmail,
            account_email=account_email,
            display_name=account_email,
            connection_status=ConnectionStatus.connected,
        )
        db.add(account)
        db.flush()

    account.display_name = account_email
    account.connection_status = ConnectionStatus.connected
    store_gmail_credentials(db, account, tokens)
    db.flush()
    return account


def list_gmail_accounts(db: Session, *, user: User) -> list[EmailAccount]:
    if user.is_local_alpha:
        return []
    statement = (
        select(EmailAccount)
        .where(
            EmailAccount.user_id == user.id,
            EmailAccount.provider == EmailAccountProvider.gmail,
        )
        .order_by(EmailAccount.id.asc())
    )
    return list(db.scalars(statement).all())


def list_runs_for_account(
    db: Session, *, user: User, account_id: int
) -> list[IngestionRun]:
    account = _get_user_gmail_account_or_raise(db, user=user, account_id=account_id)
    statement = (
        select(IngestionRun)
        .where(
            IngestionRun.user_id == user.id,
            IngestionRun.email_account_id == account.id,
        )
        .order_by(IngestionRun.id.desc())
    )
    return list(db.scalars(statement).all())


def disconnect_gmail_account(
    db: Session, *, user: User, account_id: int
) -> EmailAccount:
    account = _get_user_gmail_account_or_raise(db, user=user, account_id=account_id)
    account.credential_json = None
    account.token_expiry = None
    account.connection_status = ConnectionStatus.disconnected
    db.commit()
    db.refresh(account)
    return account


def store_gmail_credentials(
    db: Session,
    account: EmailAccount,
    tokens: dict[str, Any],
) -> None:
    access_token = tokens.get("access_token")
    if not access_token:
        raise GmailAccountDisconnectedError("Missing Gmail access token.")

    bundle = {
        "access_token": access_token,
        "refresh_token": tokens.get("refresh_token"),
        "scope": tokens.get("scope", _GMAIL_READONLY_SCOPE),
        "token_type": tokens.get("token_type", "Bearer"),
    }
    account.credential_json = encrypt_credential(json.dumps(bundle))

    expires_in = tokens.get("expires_in")
    if expires_in is not None:
        account.token_expiry = datetime.now(timezone.utc) + timedelta(
            seconds=int(expires_in)
        )
    else:
        account.token_expiry = None

    db.flush()


def get_valid_access_token(db: Session, account: EmailAccount) -> str:
    bundle = _load_credential_bundle(account)

    if account.token_expiry and account.token_expiry <= datetime.now(
        timezone.utc
    ) + timedelta(seconds=30):
        refresh_token = bundle.get("refresh_token")
        if not refresh_token:
            account.connection_status = ConnectionStatus.expired
            db.commit()
            raise GmailAccountDisconnectedError("Gmail credentials have expired.")

        refreshed_tokens = refresh_gmail_access_token(str(refresh_token))
        refreshed_tokens.setdefault("refresh_token", refresh_token)
        store_gmail_credentials(db, account, refreshed_tokens)
        account.connection_status = ConnectionStatus.connected
        db.commit()
        db.refresh(account)
        bundle = _load_credential_bundle(account)

    access_token = bundle.get("access_token")
    if not isinstance(access_token, str) or not access_token:
        raise GmailAccountDisconnectedError("Stored Gmail credentials are invalid.")
    return access_token


def granted_scopes(account: EmailAccount) -> list[str]:
    if not account.credential_json:
        return []
    try:
        bundle = _load_credential_bundle(account)
    except Exception:
        return []

    scope = bundle.get("scope")
    if not isinstance(scope, str):
        return []
    return [value for value in scope.split() if value]


def run_ingestion_scan(
    db: Session,
    *,
    user: User,
    account: EmailAccount,
    limit_count: int,
    scope: str,
) -> IngestionRun:
    if limit_count not in _ALLOWED_LIMIT_VALUES:
        raise GmailScanValidationError("Scan limit must be one of 50, 100, or 200.")
    if scope != _DEFAULT_SCOPE:
        raise GmailScanValidationError(
            "Only CATEGORY_PROMOTIONS scans are supported in ALPHA."
        )
    if account.connection_status != ConnectionStatus.connected:
        raise GmailAccountDisconnectedError("Gmail account is not connected.")

    run = IngestionRun(
        user_id=user.id,
        email_account_id=account.id,
        trigger_type=IngestionTriggerType.manual,
        status=IngestionStatus.running,
        scope=scope,
        limit_count=limit_count,
        started_at=datetime.now(timezone.utc),
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    try:
        access_token = get_valid_access_token(db, account)
        message_ids = _list_message_ids(access_token, limit_count, scope)
        grouped_sources: dict[str, _NormalizedSource] = {}

        for message_id in message_ids:
            metadata = _get_message_metadata(access_token, message_id)
            normalized = _normalize_message(metadata, default_scope=scope)
            current = grouped_sources.get(normalized.source_key)
            if current is None:
                grouped_sources[normalized.source_key] = normalized
            else:
                current.message_count += 1

        created_count = 0
        for normalized in grouped_sources.values():
            created_count += _upsert_candidate(db, account=account, source=normalized)

        run.status = IngestionStatus.completed
        run.message_count_scanned = len(message_ids)
        run.source_count_created = created_count
        run.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(run)
        return run
    except Exception as exc:
        run.status = IngestionStatus.failed
        run.error_summary = str(exc)
        run.completed_at = datetime.now(timezone.utc)
        db.commit()
        raise


def _fetch_gmail_profile(access_token: str) -> dict[str, Any]:
    response = httpx.get(
        f"{_GMAIL_API_BASE}/profile",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=15.0,
    )
    response.raise_for_status()
    return response.json()


def _get_user_gmail_account_or_raise(
    db: Session,
    *,
    user: User,
    account_id: int,
) -> EmailAccount:
    account = db.scalar(
        select(EmailAccount).where(
            EmailAccount.id == account_id,
            EmailAccount.user_id == user.id,
            EmailAccount.provider == EmailAccountProvider.gmail,
        )
    )
    if account is None:
        raise GmailAccountNotFoundError("Gmail account was not found.")
    return account


def _load_credential_bundle(account: EmailAccount) -> dict[str, Any]:
    if not account.credential_json:
        raise GmailAccountDisconnectedError("Gmail account is not connected.")
    return json.loads(decrypt_credential(account.credential_json))


def _list_message_ids(access_token: str, limit_count: int, scope: str) -> list[str]:
    response = httpx.get(
        f"{_GMAIL_API_BASE}/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        params={
            "maxResults": limit_count,
            "labelIds": scope,
        },
        timeout=20.0,
    )
    response.raise_for_status()
    payload = response.json()
    return [message["id"] for message in payload.get("messages", []) if "id" in message]


def _get_message_metadata(access_token: str, message_id: str) -> dict[str, Any]:
    response = httpx.get(
        f"{_GMAIL_API_BASE}/messages/{message_id}",
        headers={"Authorization": f"Bearer {access_token}"},
        params=[
            ("format", "metadata"),
            ("metadataHeaders", "From"),
            ("metadataHeaders", "Subject"),
        ],
        timeout=20.0,
    )
    response.raise_for_status()
    return response.json()


def _normalize_message(
    metadata: dict[str, Any], *, default_scope: str
) -> _NormalizedSource:
    headers = {
        header.get("name", ""): header.get("value", "")
        for header in metadata.get("payload", {}).get("headers", [])
    }
    from_name, from_email = parseaddr(headers.get("From", ""))
    sender_email = from_email.strip().lower() or "unknown-source@sane.local"
    source_name = from_name.strip() or sender_email
    subject = _truncate(
        headers.get("Subject") or metadata.get("snippet") or "(no subject)", 255
    )

    category = _SCOPE_LABELS.get(default_scope, "Promotions")
    if "CATEGORY_PROMOTIONS" not in metadata.get("labelIds", []):
        category = _truncate(category, 80)

    source_key = _truncate(sender_email, 160)
    return _NormalizedSource(
        source_key=source_key,
        source_name=_truncate(source_name, 140),
        sender_email=sender_email,
        representative_subject=subject,
        mailbox_category=category,
        message_count=1,
    )


def _upsert_candidate(
    db: Session, *, account: EmailAccount, source: _NormalizedSource
) -> int:
    existing = db.scalar(
        select(Candidate).where(
            Candidate.email_account_id == account.id,
            Candidate.source_key == source.source_key,
        )
    )
    classification = classify_demo_candidate(
        sender_name=source.source_name,
        sender_email=source.sender_email,
        subject=source.representative_subject,
        mailbox_category=source.mailbox_category,
    )

    if existing is not None:
        merged_emails = sorted({*existing.sender_emails, source.sender_email})
        existing.sender_emails = merged_emails
        existing.email_count = max(existing.email_count, source.message_count)
        existing.source_name = source.source_name
        existing.representative_subject = source.representative_subject
        existing.mailbox_category = source.mailbox_category
        existing.candidate_reason = classification.reason
        existing.classifier_signal = classification.signal
        existing.suggested_decision = classification.suggested_decision
        existing.confidence = classification.confidence
        db.flush()
        return 0

    db.add(
        Candidate(
            email_account_id=account.id,
            source_key=source.source_key,
            source_name=source.source_name,
            sender_emails=[source.sender_email],
            email_count=source.message_count,
            representative_subject=source.representative_subject,
            mailbox_category=source.mailbox_category,
            candidate_reason=classification.reason,
            classifier_signal=classification.signal,
            suggested_decision=classification.suggested_decision,
            confidence=classification.confidence,
        )
    )
    db.flush()
    return 1


def _require_google_oauth_config():
    settings = get_settings()
    if not settings.google_oauth_is_configured():
        raise OAuthNotConfiguredError("Google OAuth is not configured.")
    return settings


def _truncate(value: str, limit: int) -> str:
    return value[:limit]
