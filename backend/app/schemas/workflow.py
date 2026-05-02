from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import (
    CandidateSignal,
    CandidateState,
    DecisionValue,
    ExternalActionStatus,
)


class CandidateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sender_name: str
    sender_email: str
    subject: str
    mailbox_category: str
    candidate_reason: str
    classifier_signal: CandidateSignal
    suggested_decision: DecisionValue
    confidence: float | None
    processing_state: CandidateState


class CandidateSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sender_name: str
    sender_email: str
    subject: str
    processing_state: CandidateState


class CandidateListResponse(BaseModel):
    items: list[CandidateRead]


class DecisionCreate(BaseModel):
    candidate_id: int
    decision: DecisionValue
    confirmed: bool = Field(
        default=False,
        description="Explicit human confirmation is required before a decision is stored.",
    )
    note: str | None = Field(default=None, max_length=500)


class DecisionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    decision: DecisionValue
    note: str | None
    human_confirmed: bool
    external_action_status: ExternalActionStatus
    created_at: datetime
    candidate: CandidateSummary


class DecisionListResponse(BaseModel):
    items: list[DecisionRead]
