from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum as SqlEnum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import DecisionValue, ExternalActionStatus


class Decision(Base):
    __tablename__ = "decisions"

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), index=True)
    decision: Mapped[DecisionValue] = mapped_column(
        SqlEnum(DecisionValue, native_enum=False)
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    human_confirmed: Mapped[bool] = mapped_column(Boolean, default=True)
    external_action_status: Mapped[ExternalActionStatus] = mapped_column(
        SqlEnum(ExternalActionStatus, native_enum=False),
        default=ExternalActionStatus.not_executed,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    candidate = relationship("Candidate", back_populates="decisions")
