from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import IngestionStatus, IngestionTriggerType

if TYPE_CHECKING:
    from app.models.email_account import EmailAccount
    from app.models.user import User


class IngestionRun(Base):
    """A single scan/import/analyze operation against one EmailAccount.

    Records are created when an explicit scan is triggered.  No scan is
    automatically triggered on app open (A32 / A40 guardrail).

    This model exists now so the schema supports Gmail ingestion work in
    Prompt 08.  No scan logic is implemented here.
    """

    __tablename__ = "ingestion_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    email_account_id: Mapped[int] = mapped_column(
        ForeignKey("email_accounts.id"), index=True
    )
    trigger_type: Mapped[IngestionTriggerType] = mapped_column(
        SqlEnum(IngestionTriggerType, native_enum=False)
    )
    status: Mapped[IngestionStatus] = mapped_column(
        SqlEnum(IngestionStatus, native_enum=False),
        default=IngestionStatus.pending,
    )
    # Scope description, e.g. "promotions" or "all".
    scope: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Maximum number of messages to scan in one run.
    limit_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Lookback window in days.
    lookback_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    message_count_scanned: Mapped[int] = mapped_column(Integer, default=0)
    source_count_created: Mapped[int] = mapped_column(Integer, default=0)
    error_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="ingestion_runs")
    email_account: Mapped["EmailAccount"] = relationship(
        "EmailAccount", back_populates="ingestion_runs"
    )
