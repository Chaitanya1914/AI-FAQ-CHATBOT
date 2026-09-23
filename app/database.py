"""
Database configuration and session management.

Provides the SQLAlchemy engine, session maker, base class for ORM models,
and dependency functions for FastAPI.
"""
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.orm import Session

from app.config import DB_URL

# Create the SQLAlchemy engine for SQLite, allowing multi-threading
engine = create_engine(
    DB_URL, connect_args={"check_same_thread": False}
)

# Create a local session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency to get a database session.
    
    Yields:
        Session: A SQLAlchemy database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize the database by creating all tables defined in models.
    """
    # Import models here to ensure they are registered with Base before creation
    import app.models  # noqa: F401
    Base.metadata.create_all(bind=engine)
