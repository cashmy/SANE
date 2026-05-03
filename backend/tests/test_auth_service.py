from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from cryptography.hazmat.primitives.asymmetric import rsa
import jwt
import pytest
from sqlalchemy import func, select

from app.core.config import get_settings
from app.models.auth_identity import AuthIdentity
from app.models.enums import AuthProvider
from app.models.user import User
from app.models.user_email import UserEmail
from app.services.auth_service import (
    GOOGLE_ID_TOKEN_LEEWAY_SECONDS,
    GoogleIdTokenClockSkewError,
    find_or_create_user,
    verify_google_id_token,
)


def _set_google_auth_settings(monkeypatch) -> str:
    settings = get_settings()
    client_id = "google-client-id.apps.googleusercontent.com"
    monkeypatch.setattr(settings, "google_client_id", client_id)
    monkeypatch.setattr(settings, "google_client_secret", "google-client-secret")
    return client_id


def _issue_google_id_token(*, client_id: str, issued_at_offset_seconds: int):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {
            "sub": "google-sub-test",
            "iss": "https://accounts.google.com",
            "aud": client_id,
            "iat": now + timedelta(seconds=issued_at_offset_seconds),
            "exp": now + timedelta(minutes=5),
            "email": "owner@example.com",
        },
        private_key,
        algorithm="RS256",
    )
    return token, private_key.public_key()


def test_verify_google_id_token_accepts_small_clock_skew_within_leeway(
    monkeypatch,
) -> None:
    client_id = _set_google_auth_settings(monkeypatch)
    token, public_key = _issue_google_id_token(
        client_id=client_id,
        issued_at_offset_seconds=GOOGLE_ID_TOKEN_LEEWAY_SECONDS - 30,
    )
    monkeypatch.setattr(
        "app.services.auth_service.jwt.PyJWKClient",
        lambda _url: SimpleNamespace(
            get_signing_key_from_jwt=lambda _token: SimpleNamespace(key=public_key)
        ),
    )

    claims = verify_google_id_token(token)

    assert claims["sub"] == "google-sub-test"


def test_verify_google_id_token_raises_clock_skew_error_outside_leeway(
    monkeypatch,
) -> None:
    client_id = _set_google_auth_settings(monkeypatch)
    token, public_key = _issue_google_id_token(
        client_id=client_id,
        issued_at_offset_seconds=GOOGLE_ID_TOKEN_LEEWAY_SECONDS + 60,
    )
    monkeypatch.setattr(
        "app.services.auth_service.jwt.PyJWKClient",
        lambda _url: SimpleNamespace(
            get_signing_key_from_jwt=lambda _token: SimpleNamespace(key=public_key)
        ),
    )

    with pytest.raises(GoogleIdTokenClockSkewError):
        verify_google_id_token(token)


def test_find_or_create_user_creates_new_user_identity_and_verified_email(
    db_session,
) -> None:
    user = find_or_create_user(
        db_session,
        sub="google-sub-1",
        email="owner@example.com",
        name="Owner Example",
        email_verified=True,
    )
    db_session.commit()

    identity = db_session.scalar(
        select(AuthIdentity).where(AuthIdentity.provider_user_id == "google-sub-1")
    )
    email_row = db_session.scalar(
        select(UserEmail).where(
            UserEmail.user_id == user.id, UserEmail.email == "owner@example.com"
        )
    )

    assert identity is not None
    assert identity.provider == AuthProvider.google
    assert identity.user_id == user.id
    assert email_row is not None
    assert email_row.is_verified is True
    assert email_row.is_primary is True
    assert user.display_name == "Owner Example"


def test_find_or_create_user_returns_existing_identity_user(db_session) -> None:
    user = User(email="owner@example.com", display_name="Original Name")
    db_session.add(user)
    db_session.flush()
    db_session.add(
        UserEmail(
            user_id=user.id,
            email="owner@example.com",
            role="primary",
            is_primary=True,
            is_verified=True,
        )
    )
    db_session.add(
        AuthIdentity(
            user_id=user.id,
            provider=AuthProvider.google,
            provider_user_id="google-sub-2",
            provider_email="owner@example.com",
        )
    )
    db_session.commit()

    returned = find_or_create_user(
        db_session,
        sub="google-sub-2",
        email="owner@example.com",
        name="Updated Name",
        email_verified=True,
    )
    db_session.commit()

    assert returned.id == user.id
    assert returned.display_name == "Updated Name"
    assert db_session.scalar(select(func.count()).select_from(AuthIdentity)) == 1


def test_find_or_create_user_links_by_verified_user_email(db_session) -> None:
    user = User(email="verified-owner@example.com", display_name="Verified Owner")
    db_session.add(user)
    db_session.flush()
    db_session.add(
        UserEmail(
            user_id=user.id,
            email="verified@example.com",
            role="primary",
            is_primary=True,
            is_verified=True,
        )
    )
    db_session.commit()

    linked = find_or_create_user(
        db_session,
        sub="google-sub-3",
        email="verified@example.com",
        name="Verified Owner",
        email_verified=True,
    )
    db_session.commit()

    identity = db_session.scalar(
        select(AuthIdentity).where(AuthIdentity.provider_user_id == "google-sub-3")
    )

    assert linked.id == user.id
    assert identity is not None
    assert identity.user_id == user.id


def test_find_or_create_user_does_not_link_unverified_email(db_session) -> None:
    existing_user = User(
        email="unverified-owner@example.com",
        display_name="Unverified Owner",
    )
    db_session.add(existing_user)
    db_session.flush()
    db_session.add(
        UserEmail(
            user_id=existing_user.id,
            email="shared-alias@example.com",
            role="login",
            is_primary=False,
            is_verified=False,
        )
    )
    db_session.commit()

    created = find_or_create_user(
        db_session,
        sub="google-sub-4",
        email="shared-alias@example.com",
        name="New User",
        email_verified=True,
    )
    db_session.commit()

    assert created.id != existing_user.id
    assert db_session.scalar(select(func.count()).select_from(AuthIdentity)) == 1
