from sqlalchemy import func, select

from app.models.auth_identity import AuthIdentity
from app.models.enums import AuthProvider
from app.models.user import User
from app.models.user_email import UserEmail
from app.services.auth_service import find_or_create_user


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
