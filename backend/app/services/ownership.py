from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.email_account import EmailAccount
from app.models.user_email import UserEmail
from app.models.enums import ConnectionStatus, EmailAccountProvider
from app.models.user import User

settings = get_settings()

_LOCAL_ALPHA_MAILBOX_EMAIL = "local-alpha@sane.local"
_LOCAL_ALPHA_MAILBOX_NAME = "Local ALPHA Mailbox"


def get_or_create_local_alpha_user(db: Session) -> User:
    user = db.scalar(
        select(User).where(User.is_local_alpha.is_(True)).order_by(User.id.asc())
    )
    if user is not None:
        _ensure_local_alpha_user_email(db, user)
        return user

    user = User(
        display_name=settings.local_user_display_name,
        is_local_alpha=True,
    )
    db.add(user)
    db.flush()
    _ensure_local_alpha_user_email(db, user)
    return user


def _ensure_local_alpha_user_email(db: Session, user: User) -> None:
    existing = db.scalar(
        select(UserEmail).where(
            UserEmail.user_id == user.id,
            UserEmail.email == settings.local_user_email,
        )
    )
    if existing is not None:
        return

    db.add(
        UserEmail(
            user_id=user.id,
            email=settings.local_user_email,
            role="primary",
            is_primary=True,
            is_verified=True,
        )
    )


def get_or_create_local_alpha_email_account(db: Session, user: User) -> EmailAccount:
    """Return the Local ALPHA Mailbox account for *user*, creating it if absent.

    The local ALPHA email account is a synthetic mailbox used to own all demo
    sources and any data seeded outside of a real OAuth connection.  It has
    ConnectionStatus.local_only and will never be associated with live Gmail
    credentials.
    """
    account = db.scalar(
        select(EmailAccount).where(
            EmailAccount.user_id == user.id,
            EmailAccount.provider == EmailAccountProvider.local_alpha,
        )
    )
    if account is not None:
        return account

    account = EmailAccount(
        user_id=user.id,
        provider=EmailAccountProvider.local_alpha,
        account_email=_LOCAL_ALPHA_MAILBOX_EMAIL,
        display_name=_LOCAL_ALPHA_MAILBOX_NAME,
        connection_status=ConnectionStatus.local_only,
    )
    db.add(account)
    db.flush()
    return account
