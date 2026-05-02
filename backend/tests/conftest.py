from contextlib import asynccontextmanager
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import app.models
from app.db.base import Base
from app.db.session import get_db
from app.main import app

TEST_DATABASE_PATH = Path(__file__).resolve().parent / "test_runtime.db"
TEST_DATABASE_URL = f"sqlite:///{TEST_DATABASE_PATH.as_posix()}"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
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


@pytest.fixture(autouse=True)
def reset_database() -> None:
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


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
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
