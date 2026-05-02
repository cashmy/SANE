from collections.abc import Generator
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session, sessionmaker

import app.models
from app.core.config import BACKEND_DIR, get_settings
from app.db.base import Base
from app.models.user import User
from app.services.ownership import get_or_create_local_alpha_user

settings = get_settings()
ALEMBIC_CONFIG_PATH = BACKEND_DIR / "alembic.ini"
ALEMBIC_SCRIPT_LOCATION = BACKEND_DIR / "alembic"

connect_args = (
    {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)
engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, class_=Session
)


def init_db(*, use_metadata: bool = False) -> None:
    if use_metadata:
        Base.metadata.create_all(bind=engine)
        return

    table_names = set(inspect(engine).get_table_names())
    if not table_names or table_names == {"alembic_version"}:
        _upgrade_database_to_head()
        return

    if "alembic_version" in table_names:
        _upgrade_database_to_head()
        return

    if settings.database_url.startswith("sqlite"):
        _upgrade_legacy_sqlite_database()
        _stamp_database_head()
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


def _stamp_database_head() -> None:
    command.stamp(_alembic_config(), "head")


def _alembic_config() -> Config:
    config = Config(str(ALEMBIC_CONFIG_PATH))
    config.set_main_option("script_location", str(ALEMBIC_SCRIPT_LOCATION))
    config.set_main_option("sqlalchemy.url", settings.database_url)
    return config


def _upgrade_legacy_sqlite_database() -> None:
    table_names = set(inspect(engine).get_table_names())
    if "users" not in table_names:
        User.__table__.create(bind=engine)

    with SessionLocal() as db:
        local_user = get_or_create_local_alpha_user(db)
        db.commit()
        local_user_id = local_user.id

    with engine.begin() as connection:
        if "candidates" in table_names:
            candidate_columns = {
                column["name"]
                for column in inspect(connection).get_columns("candidates")
            }
            if "user_id" not in candidate_columns:
                connection.execute(
                    text("ALTER TABLE candidates ADD COLUMN user_id INTEGER")
                )
            connection.execute(
                text("UPDATE candidates SET user_id = :user_id WHERE user_id IS NULL"),
                {"user_id": local_user_id},
            )
            connection.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS ix_candidates_user_id ON candidates (user_id)"
                )
            )

        if "decisions" in table_names:
            decision_columns = {
                column["name"]
                for column in inspect(connection).get_columns("decisions")
            }
            if "user_id" not in decision_columns:
                connection.execute(
                    text("ALTER TABLE decisions ADD COLUMN user_id INTEGER")
                )
            connection.execute(
                text("UPDATE decisions SET user_id = :user_id WHERE user_id IS NULL"),
                {"user_id": local_user_id},
            )
            connection.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS ix_decisions_user_id ON decisions (user_id)"
                )
            )
