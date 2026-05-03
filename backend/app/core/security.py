from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from cryptography.fernet import Fernet
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.db.session import get_db
from app.models.user import User

SESSION_COOKIE_NAME = "sane_session"
OAUTH_STATE_COOKIE_NAME = "sane_oauth_state"
GMAIL_STATE_COOKIE_NAME = "sane_gmail_state"


def create_session_token(user_id: int) -> str:
    settings = get_settings()
    secret = _get_jwt_secret()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": f"user:{user_id}",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.jwt_expire_minutes)).timestamp()),
    }
    return jwt.encode(payload, secret, algorithm=settings.jwt_algorithm)


def decode_session_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    return jwt.decode(
        token,
        _get_jwt_secret(),
        algorithms=[settings.jwt_algorithm],
    )


def get_user_id_from_token(token: str) -> int:
    payload = decode_session_token(token)
    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject.startswith("user:"):
        raise ValueError("Session token subject is invalid.")
    try:
        return int(subject.removeprefix("user:"))
    except ValueError as exc:
        raise ValueError("Session token subject is invalid.") from exc


def create_signed_state_token(
    payload: dict[str, Any], *, expires_minutes: int = 10
) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    claims = {
        **payload,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
    }
    return jwt.encode(claims, _get_jwt_secret(), algorithm=settings.jwt_algorithm)


def decode_signed_state_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    return jwt.decode(token, _get_jwt_secret(), algorithms=[settings.jwt_algorithm])


def encrypt_credential(plaintext: str) -> str:
    return _get_fernet().encrypt(plaintext.encode("utf-8")).decode("utf-8")


def decrypt_credential(ciphertext: str) -> str:
    return _get_fernet().decrypt(ciphertext.encode("utf-8")).decode("utf-8")


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    try:
        user_id = get_user_id_from_token(token)
    except (jwt.PyJWTError, RuntimeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        ) from exc

    user = db.scalar(
        select(User).options(selectinload(User.user_emails)).where(User.id == user_id)
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    return user


def _get_jwt_secret() -> str:
    secret = get_settings().jwt_secret
    if not secret:
        raise RuntimeError("SANE_JWT_SECRET is required for session handling.")
    return secret


def _get_fernet() -> Fernet:
    key = get_settings().credential_encryption_key
    if not key:
        raise RuntimeError(
            "SANE_CREDENTIAL_ENCRYPTION_KEY is required for Gmail credential storage."
        )
    return Fernet(key.encode("utf-8"))
