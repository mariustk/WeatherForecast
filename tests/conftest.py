import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.main import app
from app.models.schedule import Base, Task


SQLALCHEMY_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if SQLALCHEMY_DATABASE_URL:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    SQLALCHEMY_DATABASE_URL = "sqlite://"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database() -> Generator[None, None, None]:
    """Create all tables before tests and drop them afterwards."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    try:
        yield
    finally:
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    """Provide a database session for a test."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session):
    """FastAPI test client with database dependency overridden."""

    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def sample_task(db_session):
    task = Task(
        name="Install sensor",
        duration="2h",
        predecessor=None,
        status="PLANNED",
        wave_height_limit=1.0,
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    return task
