from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.workflow import (
    BatchDecisionCreate,
    BatchDecisionResponse,
    DecisionCreate,
    DecisionListResponse,
    DecisionRead,
)
from app.services.workflow import (
    CandidateNotFoundError,
    HumanApprovalRequiredError,
    list_decisions,
    record_batch_decision,
    record_decision,
)

router = APIRouter(prefix="/decisions", tags=["decisions"])


@router.get("", response_model=DecisionListResponse, summary="List recorded decisions")
def read_decisions(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=5, ge=1, le=50),
    email_account_id: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> DecisionListResponse:
    result = list_decisions(
        db,
        user=user,
        page=page,
        page_size=page_size,
        email_account_id=email_account_id,
    )
    return DecisionListResponse(items=result.items, pagination=result.pagination)


@router.post(
    "/batch",
    response_model=BatchDecisionResponse,
    summary="Record human-approved batch source decisions",
)
def create_batch_decision(
    payload: BatchDecisionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> BatchDecisionResponse:
    try:
        result = record_batch_decision(db, user=user, payload=payload)
        return BatchDecisionResponse(
            applied=result.applied,
            unchanged=result.unchanged,
        )
    except HumanApprovalRequiredError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    except CandidateNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@router.post(
    "",
    response_model=DecisionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Record a human-approved decision",
)
def create_decision(
    payload: DecisionCreate,
    response: Response,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> DecisionRead:
    try:
        result = record_decision(db, user=user, payload=payload)
        if not result.applied:
            response.status_code = status.HTTP_200_OK
        return result.decision
    except HumanApprovalRequiredError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    except CandidateNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
