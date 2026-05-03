from __future__ import annotations

from secrets import token_urlsafe

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import (
    GMAIL_STATE_COOKIE_NAME,
    create_signed_state_token,
    decode_signed_state_token,
    get_current_user,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.gmail import (
    DisconnectRequest,
    EmailAccountInfo,
    IngestionRunSummary,
    ResetLocalDataRequest,
    ResetLocalDataSummary,
    ScanRequest,
)
from app.services.auth_service import OAuthNotConfiguredError
from app.services.gmail_service import (
    GmailAccountDisconnectedError,
    GmailAccountNotFoundError,
    GmailResetValidationError,
    GmailScanValidationError,
    connect_gmail_account,
    disconnect_gmail_account,
    exchange_gmail_code,
    get_gmail_connect_url,
    granted_scopes,
    list_gmail_accounts,
    list_runs_for_account,
    reset_account_local_data,
    run_ingestion_scan,
)

router = APIRouter(prefix="/gmail", tags=["gmail"])


@router.get(
    "/accounts", response_model=list[EmailAccountInfo], summary="List Gmail accounts"
)
def read_gmail_accounts(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[EmailAccountInfo]:
    accounts = list_gmail_accounts(db, user=user)
    return [
        EmailAccountInfo(
            id=account.id,
            provider=account.provider,
            account_email=account.account_email,
            display_name=account.display_name,
            connection_status=account.connection_status,
            granted_scopes=granted_scopes(account),
        )
        for account in accounts
    ]


@router.get("/connect", summary="Start Gmail connection flow")
def connect_gmail(user: User = Depends(get_current_user)) -> RedirectResponse:
    settings = get_settings()
    state = create_signed_state_token(
        {
            "purpose": "gmail_connect",
            "user_id": user.id,
            "nonce": token_urlsafe(24),
        }
    )
    try:
        response = RedirectResponse(get_gmail_connect_url(state))
    except OAuthNotConfiguredError as exc:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=str(exc),
        ) from exc

    response.set_cookie(
        GMAIL_STATE_COOKIE_NAME,
        state,
        max_age=600,
        httponly=True,
        samesite="lax",
        secure=settings.frontend_url.startswith("https://"),
    )
    return response


@router.get("/callback", summary="Handle Gmail connection callback")
def gmail_callback(
    request: Request,
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    cookie_state = request.cookies.get(GMAIL_STATE_COOKIE_NAME)
    if not cookie_state or cookie_state != state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="OAuth state is invalid."
        )

    payload = decode_signed_state_token(state)
    if payload.get("purpose") != "gmail_connect" or not isinstance(
        payload.get("user_id"), int
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="OAuth state is invalid."
        )

    user = db.get(User, int(payload["user_id"]))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required."
        )

    tokens = exchange_gmail_code(code)
    connect_gmail_account(db, user=user, tokens=tokens)
    db.commit()

    settings = get_settings()
    response = RedirectResponse(settings.frontend_url)
    response.delete_cookie(
        GMAIL_STATE_COOKIE_NAME,
        httponly=True,
        samesite="lax",
        secure=settings.frontend_url.startswith("https://"),
    )
    return response


@router.post(
    "/disconnect", status_code=status.HTTP_204_NO_CONTENT, summary="Disconnect Gmail"
)
def disconnect_gmail(
    payload: DisconnectRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Response:
    try:
        disconnect_gmail_account(db, user=user, account_id=payload.email_account_id)
    except GmailAccountNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/accounts/{account_id}/reset-local-data",
    response_model=ResetLocalDataSummary,
    summary="Reset local SANE data for one Gmail account",
)
def reset_local_data(
    account_id: int,
    payload: ResetLocalDataRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ResetLocalDataSummary:
    try:
        summary = reset_account_local_data(
            db,
            user=user,
            account_id=account_id,
            mode=payload.mode,
            confirmed=payload.confirmed,
        )
        return ResetLocalDataSummary.model_validate(summary)
    except GmailAccountNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except GmailResetValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc


@router.post(
    "/scan", response_model=IngestionRunSummary, summary="Run a manual Gmail scan"
)
def scan_gmail(
    payload: ScanRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> IngestionRunSummary:
    try:
        accounts = {
            account.id: account for account in list_gmail_accounts(db, user=user)
        }
        account = accounts.get(payload.email_account_id)
        if account is None:
            raise GmailAccountNotFoundError("Gmail account was not found.")
        run = run_ingestion_scan(
            db,
            user=user,
            account=account,
            limit_count=payload.limit_count,
            scope=payload.scope,
        )
        return IngestionRunSummary.model_validate(run)
    except GmailAccountNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except GmailAccountDisconnectedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc
    except GmailScanValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc


@router.get(
    "/runs/{account_id}",
    response_model=list[IngestionRunSummary],
    summary="List ingestion runs",
)
def read_runs(
    account_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[IngestionRunSummary]:
    try:
        runs = list_runs_for_account(db, user=user, account_id=account_id)
    except GmailAccountNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    return [IngestionRunSummary.model_validate(run) for run in runs]
