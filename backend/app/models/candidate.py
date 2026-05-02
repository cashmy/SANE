from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SqlEnum, Float, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import CandidateSignal, CandidateState, DecisionValue

if TYPE_CHECKING:
    from app.models.decision import Decision


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(primary_key=True)
    sender_name: Mapped[str] = mapped_column(String(140))
    sender_email: Mapped[str] = mapped_column(String(255))
    subject: Mapped[str] = mapped_column(String(255))
    mailbox_category: Mapped[str] = mapped_column(String(80))
    candidate_reason: Mapped[str] = mapped_column(Text)
    classifier_signal: Mapped[CandidateSignal] = mapped_column(
        SqlEnum(CandidateSignal, native_enum=False)
    )
    suggested_decision: Mapped[DecisionValue] = mapped_column(
        SqlEnum(DecisionValue, native_enum=False)
    )
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    processing_state: Mapped[CandidateState] = mapped_column(
        SqlEnum(CandidateState, native_enum=False),
        default=CandidateState.pending_review,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    decisions: Mapped[list["Decision"]] = relationship(
        back_populates="candidate", cascade="all, delete-orphan"
    )
