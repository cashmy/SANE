from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    JSON,
    DateTime,
    Enum as SqlEnum,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import CandidateSignal, CandidateState, DecisionValue

if TYPE_CHECKING:
    from app.models.decision import Decision
    from app.models.email_account import EmailAccount


class Candidate(Base):
    __tablename__ = "candidates"
    __table_args__ = (
        # Source identity is scoped to the email account (A40).
        # unique(email_account_id, source_key) replaces the earlier user-scoped rule.
        Index(
            "ix_candidates_email_account_id_source_key",
            "email_account_id",
            "source_key",
            unique=True,
        ),
    )
    # Internal SQLAlchemy name retained to reduce ALPHA churn; external contracts use source language.

    id: Mapped[int] = mapped_column(primary_key=True)
    email_account_id: Mapped[int] = mapped_column(
        ForeignKey("email_accounts.id"), index=True
    )
    source_key: Mapped[str] = mapped_column(String(160))
    source_name: Mapped[str] = mapped_column(String(140))
    sender_emails: Mapped[list[str]] = mapped_column(JSON)
    email_count: Mapped[int]
    representative_subject: Mapped[str] = mapped_column(String(255))
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
    email_account: Mapped["EmailAccount"] = relationship(
        "EmailAccount", back_populates="candidates"
    )

    @property
    def current_decision(self) -> DecisionValue | None:
        latest = max(self.decisions, key=lambda decision: decision.id, default=None)
        if latest is None:
            return None
        return latest.decision
