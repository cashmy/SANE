from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

import httpx
import jwt
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.models.auth_identity import AuthIdentity
from app.models.enums import AuthProvider
from app.models.user import User
from app.models.user_email import UserEmail

_GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
_GOOGLE_JWKS_URL = "https://www.googleapis.com/oauth2/v3/certs"
_GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
_GOOGLE_SIGNIN_SCOPES = ["openid", "email", "profile"]
_GOOGLE_ISSUERS = {"accounts.google.com", "https://accounts.google.com"}
GOOGLE_ID_TOKEN_LEEWAY_SECONDS = 120
GOOGLE_CLOCK_SKEW_ERROR_MESSAGE = (
    "Google sign-in could not be completed because this device clock appears out "
    "of sync. Sync your system time and try again."
)


class OAuthNotConfiguredError(RuntimeError):
    pass


class GoogleIdTokenClockSkewError(RuntimeError):
    pass


def get_google_auth_url(state: str) -> str:
    settings = _require_google_oauth_config()
    query = urlencode(
        {
            "client_id": settings.google_client_id,
            "redirect_uri": settings.oauth_redirect_uri,
            "response_type": "code",
            "scope": " ".join(_GOOGLE_SIGNIN_SCOPES),
            "state": state,
            "access_type": "offline",
            "include_granted_scopes": "true",
            "prompt": "select_account",
        }
    )
    return f"{_GOOGLE_AUTH_URL}?{query}"


def exchange_google_code(code: str) -> dict[str, Any]:
    settings = _require_google_oauth_config()
    response = httpx.post(
        _GOOGLE_TOKEN_URL,
        data={
            "code": code,
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uri": settings.oauth_redirect_uri,
            "grant_type": "authorization_code",
        },
        timeout=15.0,
    )
    response.raise_for_status()
    return response.json()


def verify_google_id_token(id_token: str) -> dict[str, Any]:
    settings = _require_google_oauth_config()
    jwks_client = jwt.PyJWKClient(_GOOGLE_JWKS_URL)
    signing_key = jwks_client.get_signing_key_from_jwt(id_token)
    try:
        claims = jwt.decode(
            id_token,
            signing_key.key,
            algorithms=["RS256"],
            audience=settings.google_client_id,
            leeway=GOOGLE_ID_TOKEN_LEEWAY_SECONDS,
            options={"require": ["sub", "iss"]},
        )
    except jwt.ImmatureSignatureError as exc:
        raise GoogleIdTokenClockSkewError(GOOGLE_CLOCK_SKEW_ERROR_MESSAGE) from exc

    issuer = claims.get("iss")
    if issuer not in _GOOGLE_ISSUERS:
        raise jwt.InvalidIssuerError("Google token issuer is invalid.")
    return claims


def find_or_create_user(
    db: Session,
    *,
    sub: str,
    email: str | None,
    name: str | None,
    email_verified: bool,
) -> User:
    normalized_email = _normalize_email(email)

    identity = db.scalar(
        select(AuthIdentity)
        .options(
            selectinload(AuthIdentity.user).selectinload(User.user_emails),
        )
        .where(
            AuthIdentity.provider == AuthProvider.google,
            AuthIdentity.provider_user_id == sub,
        )
    )
    if identity is not None:
        user = identity.user
        identity.provider_email = normalized_email
        _sync_user_profile(user, name=name, email=normalized_email)
        if normalized_email:
            _upsert_user_email(
                db,
                user=user,
                email=normalized_email,
                is_verified=email_verified,
            )
        db.flush()
        return user

    linked_user: User | None = None
    if normalized_email and email_verified:
        matched_email = db.scalar(
            select(UserEmail)
            .options(selectinload(UserEmail.user).selectinload(User.user_emails))
            .where(
                UserEmail.email == normalized_email,
                UserEmail.is_verified.is_(True),
            )
        )
        if matched_email is not None:
            linked_user = matched_email.user

    if linked_user is None:
        linked_user = User(
            email=normalized_email,
            display_name=name or normalized_email or "SANE User",
            is_local_alpha=False,
        )
        db.add(linked_user)
        db.flush()

    _sync_user_profile(linked_user, name=name, email=normalized_email)
    if normalized_email:
        _upsert_user_email(
            db,
            user=linked_user,
            email=normalized_email,
            is_verified=email_verified,
        )

    db.add(
        AuthIdentity(
            user_id=linked_user.id,
            provider=AuthProvider.google,
            provider_user_id=sub,
            provider_email=normalized_email,
        )
    )
    db.flush()
    return linked_user


def primary_user_email(user: User) -> str | None:
    primary = next((email for email in user.user_emails if email.is_primary), None)
    if primary is not None:
        return primary.email
    if user.user_emails:
        return user.user_emails[0].email
    return user.email


def _normalize_email(email: str | None) -> str | None:
    if not email:
        return None
    normalized = email.strip().lower()
    return normalized or None


def _require_google_oauth_config():
    settings = get_settings()
    if not settings.google_oauth_is_configured():
        raise OAuthNotConfiguredError("Google OAuth is not configured.")
    return settings


def _sync_user_profile(user: User, *, name: str | None, email: str | None) -> None:
    if name:
        user.display_name = name
    if email and (user.email is None or user.email == email):
        user.email = email


def _upsert_user_email(
    db: Session,
    *,
    user: User,
    email: str,
    is_verified: bool,
) -> None:
    existing = db.scalar(
        select(UserEmail).where(UserEmail.user_id == user.id, UserEmail.email == email)
    )
    if existing is not None:
        existing.is_verified = existing.is_verified or is_verified
        if not any(candidate.is_primary for candidate in user.user_emails):
            existing.is_primary = True
            existing.role = "primary"
        return

    has_primary = any(candidate.is_primary for candidate in user.user_emails)
    db.add(
        UserEmail(
            user_id=user.id,
            email=email,
            role="primary" if not has_primary else "login",
            is_primary=not has_primary,
            is_verified=is_verified,
        )
    )
