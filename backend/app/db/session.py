from collections.abc import Generator

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session, sessionmaker

import app.models
from app.core.config import BACKEND_DIR, get_settings
from app.db.base import Base

settings = get_settings()
ALEMBIC_CONFIG_PATH = BACKEND_DIR / "alembic.ini"
ALEMBIC_SCRIPT_LOCATION = BACKEND_DIR / "alembic"

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, class_=Session
)


def init_db(*, use_metadata: bool = False) -> None:
    if use_metadata:
        Base.metadata.create_all(bind=engine)
        return

    if settings.database_url.startswith("sqlite"):
        raise RuntimeError(
            "SQLite is deprecated for normal SANE runtime. Configure"
            " SANE_DATABASE_URL with a PostgreSQL URL."
        )

    table_names = set(inspect(engine).get_table_names())
    if not table_names or table_names == {"alembic_version"}:
        _upgrade_database_to_head()
        return

    if "alembic_version" in table_names:
        _upgrade_database_to_head()
        return

    raise RuntimeError(
        "Database schema exists but is not under Alembic control. Apply the"
        " initial migration or reset the database before starting the app."
    )


def reset_db() -> None:
    Base.metadata.drop_all(bind=engine)
    with engine.begin() as connection:
        if inspect(connection).has_table("alembic_version"):
            connection.execute(text("DROP TABLE alembic_version"))


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _upgrade_database_to_head() -> None:
    command.upgrade(_alembic_config(), "head")


def _alembic_config() -> Config:
    config = Config(str(ALEMBIC_CONFIG_PATH))
    config.set_main_option("script_location", str(ALEMBIC_SCRIPT_LOCATION))
    config.set_main_option("sqlalchemy.url", settings.database_url)
    config.attributes["sane_database_url"] = settings.database_url
    return config
