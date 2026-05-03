from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ConnectionStatus, EmailAccountProvider, IngestionStatus


class EmailAccountInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    provider: EmailAccountProvider
    account_email: str
    display_name: str
    connection_status: ConnectionStatus
    granted_scopes: list[str] = Field(default_factory=list)


class IngestionRunSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: IngestionStatus
    scope: str | None
    limit_count: int | None
    message_count_scanned: int
    source_count_seen: int
    source_count_created: int
    error_summary: str | None
    started_at: datetime | None
    completed_at: datetime | None


class DisconnectRequest(BaseModel):
    email_account_id: int


class ScanRequest(BaseModel):
    email_account_id: int
    limit_count: int = 50
    scope: str = "CATEGORY_PROMOTIONS"


ResetLocalDataMode = Literal["sources_only", "sources_and_decisions"]


class ResetLocalDataRequest(BaseModel):
    mode: ResetLocalDataMode
    confirmed: bool = False


class ResetLocalDataSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_id: int
    account_email: str
    mode: ResetLocalDataMode
    sources_deleted: int
    decisions_deleted: int
    ingestion_runs_preserved: int
    ingestion_runs_deleted: int
