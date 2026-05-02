from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.workflow import CandidateListResponse
from app.services.workflow import list_candidates

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.get("", response_model=CandidateListResponse, summary="List review candidates")
def read_candidates(
    include_processed: bool = Query(default=False),
    db: Session = Depends(get_db),
) -> CandidateListResponse:
    return CandidateListResponse(
        items=list_candidates(db, include_processed=include_processed)
    )
