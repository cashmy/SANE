from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]
DEFAULT_SQLITE_PATH = BACKEND_DIR / "sane_alpha.db"
DEFAULT_DATABASE_URL = f"sqlite:///{DEFAULT_SQLITE_PATH.as_posix()}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_prefix="SANE_",
        extra="ignore",
    )

    app_name: str = "SANE API"
    debug: bool = True
    api_prefix: str = "/api"
    database_url: str = DEFAULT_DATABASE_URL
    cors_origins: list[str] = ["http://localhost:5173"]
    local_user_email: str = "local-alpha@sane.local"
    local_user_display_name: str = "Local ALPHA User"


@lru_cache
def get_settings() -> Settings:
    return Settings()
