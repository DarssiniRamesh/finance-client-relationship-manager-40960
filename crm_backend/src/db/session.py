from __future__ import annotations

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.api.config import get_settings

settings = get_settings()

# For SQLite, need check_same_thread=False for multithreaded FastAPI use.
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

# Create engine and session factory.
engine = create_engine(settings.DATABASE_URL, echo=False, future=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


# PUBLIC_INTERFACE
def get_db() -> Generator[Session, None, None]:
    """Yield a SQLAlchemy session for request scope and ensure cleanup."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        # Ensure the connection is properly closed.
        db.close()
