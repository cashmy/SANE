from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import (
    CandidateSignal,
    CandidateState,
    DecisionValue,
    ExternalActionStatus,
)


class PaginationMeta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_previous: bool
    has_next: bool


class SourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_key: str
    source_name: str
    sender_emails: list[str]
    email_count: int
    representative_subject: str
    mailbox_category: str
    candidate_reason: str
    classifier_signal: CandidateSignal
    suggested_decision: DecisionValue
    current_decision: DecisionValue | None
    confidence: float | None
    processing_state: CandidateState


class SourceSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_key: str
    source_name: str
    sender_emails: list[str]
    email_count: int
    representative_subject: str
    mailbox_category: str
    current_decision: DecisionValue | None
    processing_state: CandidateState


class SourceListResponse(BaseModel):
    items: list[SourceRead]
    pagination: PaginationMeta
    available_categories: list[str]


class DecisionCreate(BaseModel):
    source_id: int
    decision: DecisionValue
    confirmed: bool = Field(
        default=False,
        description="Explicit human confirmation is required before a decision is stored.",
    )
    note: str | None = Field(default=None, max_length=500)


class BatchDecisionCreate(BaseModel):
    source_ids: list[int] = Field(min_length=1, max_length=100)
    decision: DecisionValue
    confirmed: bool = Field(
        default=False,
        description="Explicit human confirmation is required before a decision is stored.",
    )
    note: str | None = Field(default=None, max_length=500)


class DecisionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    revised_from_decision_id: int | None
    decision: DecisionValue
    note: str | None
    human_confirmed: bool
    external_action_status: ExternalActionStatus
    created_at: datetime
    is_current: bool
    is_revision: bool
    source: SourceSummary


class DecisionListResponse(BaseModel):
    items: list[DecisionRead]
    pagination: PaginationMeta


class BatchDecisionResponse(BaseModel):
    applied: list[DecisionRead]
    unchanged: list[DecisionRead]
