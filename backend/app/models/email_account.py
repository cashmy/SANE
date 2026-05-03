from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import ConnectionStatus, EmailAccountProvider

if TYPE_CHECKING:
    from app.models.candidate import Candidate
    from app.models.ingestion_run import IngestionRun
    from app.models.user import User


class EmailAccount(Base):
    """A connected mailbox registered to a SANE user.

    Connecting a mailbox does not imply a particular sign-in method; that is
    modelled by AuthIdentity.  One user can have multiple EmailAccount records
    (e.g. personal Gmail + work Gmail).

    connection_status lifecycle:
      connected   — active, scans/imports are allowed
      disconnected — user-initiated pause; local data preserved
      expired     — OAuth token expired; reauth needed
      revoked     — OAuth access revoked by user or provider
      error       — provider error; investigation needed
      local_only  — no external provider; used for demo/ALPHA data
    """

    __tablename__ = "email_accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    provider: Mapped[EmailAccountProvider] = mapped_column(
        SqlEnum(EmailAccountProvider, native_enum=False)
    )
    account_email: Mapped[str] = mapped_column(String(255), index=True)
    display_name: Mapped[str] = mapped_column(String(120))
    connection_status: Mapped[ConnectionStatus] = mapped_column(
        SqlEnum(ConnectionStatus, native_enum=False),
        default=ConnectionStatus.local_only,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="email_accounts")
    candidates: Mapped[list["Candidate"]] = relationship(
        back_populates="email_account", cascade="all, delete-orphan"
    )
    ingestion_runs: Mapped[list["IngestionRun"]] = relationship(
        back_populates="email_account", cascade="all, delete-orphan"
    )
