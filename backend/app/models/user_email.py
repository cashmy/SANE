from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum as SqlEnum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import UserEmailRole

if TYPE_CHECKING:
    from app.models.user import User


class UserEmail(Base):
    """An email address associated with a SANE user account.

    A user may have multiple addresses with different roles (primary, contact,
    recovery).  Verification state tracks whether the address has been confirmed.
    """

    __tablename__ = "user_emails"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    email: Mapped[str] = mapped_column(String(255), index=True)
    role: Mapped[UserEmailRole] = mapped_column(
        SqlEnum(UserEmailRole, native_enum=False, validate_strings=True),
        default=UserEmailRole.contact,
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="user_emails")
