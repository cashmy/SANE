from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.user import User

settings = get_settings()


def get_or_create_local_alpha_user(db: Session) -> User:
    user = db.scalar(select(User).where(User.email == settings.local_user_email))
    if user is not None:
        return user

    user = User(
        email=settings.local_user_email,
        display_name=settings.local_user_display_name,
        is_local_alpha=True,
    )
    db.add(user)
    db.flush()
    return user
