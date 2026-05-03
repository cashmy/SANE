from __future__ import annotations

from secrets import token_urlsafe

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import JSONResponse, RedirectResponse
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
from app.schemas.auth import AuthConfig, UserMe
from app.services.auth_service import (
    OAuthNotConfiguredError,
    exchange_google_code,
    find_or_create_user,
    get_google_auth_url,
    primary_user_email,
    verify_google_id_token,
)
from app.services.ownership import get_or_create_local_alpha_user

router = APIRouter(prefix="/auth", tags=["auth"])

_GOOGLE_OAUTH_LOCAL_MESSAGE = (
    "Google OAuth is not configured for this local environment."
)
_LOCAL_DEV_AUTH_DISABLED_DETAIL = "Local development auth is not enabled."
_LOCAL_DEV_AUTH_BLOCKED_DETAIL = (
    "Local development auth is blocked outside development."
)


def _google_oauth_enabled() -> bool:
    settings = get_settings()
    return bool(settings.google_client_id and settings.google_client_secret)


def _local_dev_auth_enabled() -> bool:
    settings = get_settings()
    return settings.auth_mode == "local_dev" and settings.debug


def _serialize_user(user: User) -> UserMe:
    return UserMe(
        id=user.id,
        email=primary_user_email(user),
        display_name=user.display_name,
        is_local_alpha=user.is_local_alpha,
    )


@router.get("/config", response_model=AuthConfig, summary="Return auth config")
def read_auth_config() -> AuthConfig:
    settings = get_settings()
    google_oauth_enabled = _google_oauth_enabled()
    return AuthConfig(
        auth_mode=settings.auth_mode,
        local_dev_enabled=_local_dev_auth_enabled(),
        google_oauth_enabled=google_oauth_enabled,
        google_oauth_message=(
            None if google_oauth_enabled else _GOOGLE_OAUTH_LOCAL_MESSAGE
        ),
    )


@router.post(
    "/local-dev/login",
    response_model=UserMe,
    summary="Create a Local ALPHA session in development",
)
def local_dev_login(db: Session = Depends(get_db)) -> JSONResponse:
    settings = get_settings()
    if settings.auth_mode != "local_dev":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_LOCAL_DEV_AUTH_DISABLED_DETAIL,
        )
    if not settings.debug:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=_LOCAL_DEV_AUTH_BLOCKED_DETAIL,
        )

    user = get_or_create_local_alpha_user(db)
    db.commit()
    payload = _serialize_user(user)

    response = JSONResponse(payload.model_dump())
    response.set_cookie(
        SESSION_COOKIE_NAME,
        create_session_token(user.id),
        max_age=settings.jwt_expire_minutes * 60,
        httponly=True,
        samesite="lax",
        secure=settings.frontend_url.startswith("https://"),
    )
    return response


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
    return _serialize_user(user)


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
