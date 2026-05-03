from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import AuthProvider

if TYPE_CHECKING:
    from app.models.user import User


class AuthIdentity(Base):
    """A sign-in identity record for a SANE user.

    Tracks how a user can authenticate.  Having an auth identity does not
    imply mailbox access; that is modelled separately by EmailAccount.
    Multiple auth identities are allowed per user (e.g. Google + GitHub).
    """

    __tablename__ = "auth_identities"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    provider: Mapped[AuthProvider] = mapped_column(
        SqlEnum(AuthProvider, native_enum=False)
    )
    # Provider-issued user identifier (e.g. Google sub claim).  May be null
    # for local_dev / magic_link providers before first successful sign-in.
    provider_user_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True
    )
    # Email address reported by the provider at sign-in time.
    provider_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="auth_identities")
