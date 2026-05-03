from __future__ import annotations

from secrets import token_urlsafe

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import (
    OAUTH_STATE_COOKIE_NAME,
    SESSION_COOKIE_NAME,
    create_session_token,
    get_current_user,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import UserMe
from app.services.auth_service import (
    OAuthNotConfiguredError,
    exchange_google_code,
    find_or_create_user,
    get_google_auth_url,
    primary_user_email,
    verify_google_id_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/google/login", summary="Start Google sign-in")
def google_login() -> RedirectResponse:
    settings = get_settings()
    state = token_urlsafe(24)
    try:
        response = RedirectResponse(get_google_auth_url(state))
    except OAuthNotConfiguredError as exc:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=str(exc),
        ) from exc

    response.set_cookie(
        OAUTH_STATE_COOKIE_NAME,
        state,
        max_age=600,
        httponly=True,
        samesite="lax",
        secure=settings.frontend_url.startswith("https://"),
    )
    return response


@router.get("/google/callback", summary="Handle Google sign-in callback")
def google_callback(
    request: Request,
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    settings = get_settings()
    cookie_state = request.cookies.get(OAUTH_STATE_COOKIE_NAME)
    if not cookie_state or cookie_state != state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OAuth state is invalid.",
        )

    token_payload = exchange_google_code(code)
    id_token = token_payload.get("id_token")
    if not isinstance(id_token, str) or not id_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google sign-in response did not include an ID token.",
        )

    claims = verify_google_id_token(id_token)
    sub = claims.get("sub")
    if not isinstance(sub, str) or not sub:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google sign-in response did not include a subject.",
        )

    user = find_or_create_user(
        db,
        sub=sub,
        email=claims.get("email") if isinstance(claims.get("email"), str) else None,
        name=claims.get("name") if isinstance(claims.get("name"), str) else None,
        email_verified=bool(claims.get("email_verified", False)),
    )
    db.commit()

    response = RedirectResponse(settings.frontend_url)
    response.set_cookie(
        SESSION_COOKIE_NAME,
        create_session_token(user.id),
        max_age=settings.jwt_expire_minutes * 60,
        httponly=True,
        samesite="lax",
        secure=settings.frontend_url.startswith("https://"),
    )
    response.delete_cookie(
        OAUTH_STATE_COOKIE_NAME,
        httponly=True,
        samesite="lax",
        secure=settings.frontend_url.startswith("https://"),
    )
    return response


@router.get("/me", response_model=UserMe, summary="Return the current signed-in user")
def read_me(user: User = Depends(get_current_user)) -> UserMe:
    return UserMe(
        id=user.id,
        email=primary_user_email(user),
        display_name=user.display_name,
        is_local_alpha=user.is_local_alpha,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, summary="Sign out")
def logout() -> Response:
    settings = get_settings()
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie(
        SESSION_COOKIE_NAME,
        httponly=True,
        samesite="lax",
        secure=settings.frontend_url.startswith("https://"),
    )
    return response
