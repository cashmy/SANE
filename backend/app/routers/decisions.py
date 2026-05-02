from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.workflow import DecisionCreate, DecisionListResponse, DecisionRead
from app.services.workflow import (
    CandidateNotFoundError,
    HumanApprovalRequiredError,
    list_decisions,
    record_decision,
)

router = APIRouter(prefix="/decisions", tags=["decisions"])


@router.get("", response_model=DecisionListResponse, summary="List recorded decisions")
def read_decisions(db: Session = Depends(get_db)) -> DecisionListResponse:
    return DecisionListResponse(items=list_decisions(db))


@router.post(
    "",
    response_model=DecisionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Record a human-approved decision",
)
def create_decision(
    payload: DecisionCreate,
    db: Session = Depends(get_db),
) -> DecisionRead:
    try:
        return record_decision(db, payload)
    except HumanApprovalRequiredError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    except CandidateNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
