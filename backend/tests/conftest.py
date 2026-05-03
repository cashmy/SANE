import os
from contextlib import asynccontextmanager

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.orm import Session, sessionmaker

os.environ.setdefault(
    "SANE_JWT_SECRET",
    "test-jwt-secret-with-32-byte-minimum-length",
)
os.environ.setdefault(
    "SANE_CREDENTIAL_ENCRYPTION_KEY",
    "MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY=",
)

import app.models
from app.core.config import BACKEND_DIR, get_settings
from app.core.security import SESSION_COOKIE_NAME, create_session_token
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import User
from app.models.user_email import UserEmail
from app.services.ownership import get_or_create_local_alpha_user


def _require_safe_test_database_url(
    test_database_url: str | None,
    runtime_database_url: str,
) -> str:
    if not test_database_url:
        raise RuntimeError(
            "SANE_TEST_DATABASE_URL is required for backend pytest and must point"
            " to a dedicated PostgreSQL test database."
        )

    test_url = make_url(test_database_url)
    runtime_url = make_url(runtime_database_url)

    if test_url.get_backend_name() != "postgresql":
        raise RuntimeError(
            "SANE_TEST_DATABASE_URL must use a PostgreSQL URL. SQLite is no longer"
            " supported for backend persistence or API validation tests."
        )

    if _database_identity(test_url) == _database_identity(runtime_url):
        raise RuntimeError(
            "SANE_TEST_DATABASE_URL must not equal SANE_DATABASE_URL. Backend tests"
            " require a separate PostgreSQL database."
        )

    database_name = (test_url.database or "").lower()
    if "test" not in database_name:
        raise RuntimeError(
            "SANE_TEST_DATABASE_URL must target a database whose name includes"
            " 'test' so destructive resets cannot point at the runtime database."
        )

    return test_database_url


def _database_identity(url: URL) -> tuple[str | None, ...]:
    return (
        url.drivername,
        url.username,
        url.password,
        url.host,
        str(url.port) if url.port is not None else None,
        url.database,
    )


def _alembic_config(database_url: str) -> Config:
    config = Config(str(ALEMBIC_CONFIG_PATH))
    config.set_main_option("script_location", str(ALEMBIC_SCRIPT_LOCATION))
    config.set_main_option("sqlalchemy.url", database_url)
    config.attributes["sane_database_url"] = database_url
    return config


def _upgrade_test_database_to_head() -> None:
    command.upgrade(_alembic_config(TEST_DATABASE_URL), "head")


def _truncate_test_tables() -> None:
    table_names = [
        test_engine.dialect.identifier_preparer.format_table(table)
        for table in Base.metadata.sorted_tables
    ]
    if not table_names:
        return

    with test_engine.begin() as connection:
        connection.execute(
            text(
                "TRUNCATE TABLE " + ", ".join(table_names) + " RESTART IDENTITY CASCADE"
            )
        )


settings = get_settings()
RUNTIME_DATABASE_URL = settings.database_url
TEST_DATABASE_URL = _require_safe_test_database_url(
    settings.test_database_url,
    RUNTIME_DATABASE_URL,
)
ALEMBIC_CONFIG_PATH = BACKEND_DIR / "alembic.ini"
ALEMBIC_SCRIPT_LOCATION = BACKEND_DIR / "alembic"

test_engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True,
)
TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
    class_=Session,
)


@asynccontextmanager
async def _test_lifespan(_: object):
    yield


def _override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def prepare_test_database() -> None:
    _upgrade_test_database_to_head()
    _truncate_test_tables()
    yield
    test_engine.dispose()


@pytest.fixture(autouse=True)
def reset_database() -> None:
    _truncate_test_tables()
    yield


@pytest.fixture
def client() -> TestClient:
    original_lifespan = app.router.lifespan_context
    app.router.lifespan_context = _test_lifespan
    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    app.router.lifespan_context = original_lifespan


@pytest.fixture
def auth_client(client: TestClient, db_session: Session) -> TestClient:
    user = get_or_create_local_alpha_user(db_session)
    db_session.commit()
    client.cookies.set(
        SESSION_COOKIE_NAME,
        create_session_token(user.id),
        path="/",
    )
    return client


@pytest.fixture
def authenticated_client_factory(client: TestClient, db_session: Session):
    def _make(
        *,
        email: str = "signed-in-user@example.com",
        display_name: str = "Signed In User",
        is_local_alpha: bool = False,
    ) -> tuple[TestClient, User]:
        user = User(
            email=email,
            display_name=display_name,
            is_local_alpha=is_local_alpha,
        )
        db_session.add(user)
        db_session.flush()
        db_session.add(
            UserEmail(
                user_id=user.id,
                email=email,
                role="primary",
                is_primary=True,
                is_verified=True,
            )
        )
        db_session.commit()
        client.cookies.set(
            SESSION_COOKIE_NAME,
            create_session_token(user.id),
            path="/",
        )
        return client, user

    return _make


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
