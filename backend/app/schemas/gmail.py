from datetime import datetime

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
