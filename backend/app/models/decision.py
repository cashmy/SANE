from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum as SqlEnum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import DecisionValue, ExternalActionStatus

if TYPE_CHECKING:
    from app.models.candidate import Candidate
    from app.models.user import User


class Decision(Base):
    __tablename__ = "decisions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), index=True)
    revised_from_decision_id: Mapped[int | None] = mapped_column(
        ForeignKey("decisions.id"), nullable=True, index=True
    )
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

    candidate: Mapped["Candidate"] = relationship(
        "Candidate", back_populates="decisions"
    )
    user: Mapped["User"] = relationship("User", back_populates="decisions")
    previous_decision = relationship("Decision", remote_side="Decision.id")

    @property
    def source(self) -> "Candidate":
        return self.candidate

    @property
    def is_revision(self) -> bool:
        return self.revised_from_decision_id is not None

    @property
    def is_current(self) -> bool:
        if not self.candidate.decisions:
            return True
        latest_id = max(decision.id for decision in self.candidate.decisions)
        return self.id == latest_id
