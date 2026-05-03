from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.auth_identity import AuthIdentity
    from app.models.decision import Decision
    from app.models.email_account import EmailAccount
    from app.models.ingestion_run import IngestionRun
    from app.models.user_email import UserEmail


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    display_name: Mapped[str] = mapped_column(String(120))
    is_local_alpha: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Decision.user_id is kept as a direct FK for query/authorization convenience.
    # The invariant is: Decision.user_id == Source -> EmailAccount.user_id.
    decisions: Mapped[list["Decision"]] = relationship(back_populates="user")
    user_emails: Mapped[list["UserEmail"]] = relationship(back_populates="user")
    auth_identities: Mapped[list["AuthIdentity"]] = relationship(back_populates="user")
    email_accounts: Mapped[list["EmailAccount"]] = relationship(back_populates="user")
    ingestion_runs: Mapped[list["IngestionRun"]] = relationship(back_populates="user")
