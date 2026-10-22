"""
Test setup: every test gets a fresh in-memory database with the seed data.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.db import get_session
from app.main import app
from app.seed import seed


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        seed(session)

    def get_test_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_test_session
    yield TestClient(app)  # not used as a context manager, so the real DB file is never touched
    app.dependency_overrides.clear()


# Seeded users: 1 = Alex, 2 = Bea, 3 = Chris
ALEX = {"X-User-Id": "1"}
BEA = {"X-User-Id": "2"}
CHRIS = {"X-User-Id": "3"}
