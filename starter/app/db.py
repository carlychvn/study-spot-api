"""
Database setup.

We use SQLite (the whole database is one file, nothing to install) and
SQLModel (tables are Python classes, so you don't need to write SQL).
"""
import os

from sqlmodel import Session, SQLModel, create_engine

# The database lives in this file next to your code.
# Delete the file (or run `python seed.py`) to start fresh.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # needed for SQLite + FastAPI
)


def create_tables() -> None:
    """Create every table defined in models.py (does nothing if they already exist)."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    PATTERN: dependency.
    Any route that needs the database adds `session: Session = Depends(get_session)`.
    FastAPI opens a session for that request and closes it afterwards.
    """
    with Session(engine) as session:
        yield session
