from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.enums import CandidateSignal
from app.schemas.workflow import SourceListResponse
from app.services.workflow import list_sources

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("", response_model=SourceListResponse, summary="List review sources")
def read_sources(
    include_processed: bool = Query(default=False),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=5, ge=1, le=50),
    search: str | None = Query(default=None),
    category: str | None = Query(default=None),
    signal: CandidateSignal | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> SourceListResponse:
    result = list_sources(
        db,
        user=user,
        include_processed=include_processed,
        page=page,
        page_size=page_size,
        search=search,
        category=category,
        signal=signal,
    )
    return SourceListResponse(
        items=result.items,
        pagination=result.pagination,
        available_categories=result.available_categories,
    )
