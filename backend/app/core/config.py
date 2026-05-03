from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_prefix="SANE_",
        extra="ignore",
    )

    app_name: str = "SANE API"
    debug: bool = True
    auth_mode: Literal["google_oauth", "local_dev"] = "google_oauth"
    api_prefix: str = "/api"
    database_url: str
    test_database_url: str | None = None
    cors_origins: list[str] = ["http://localhost:5173"]
    local_user_email: str = "local-alpha@sane.local"
    local_user_display_name: str = "Local ALPHA User"
    frontend_url: str = "http://localhost:5173"
    jwt_secret: str | None = None
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7
    credential_encryption_key: str | None = None
    google_client_id: str | None = None
    google_client_secret: str | None = None
    oauth_redirect_uri: str = "http://localhost:8000/api/auth/google/callback"
    gmail_redirect_uri: str = "http://localhost:8000/api/gmail/callback"


@lru_cache
def get_settings() -> Settings:
    return Settings()
