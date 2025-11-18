from __future__ import annotations

from sqlalchemy.engine import Engine

from src.db.models import Base


# PUBLIC_INTERFACE
def init_db(engine: Engine) -> None:
    """Create database tables if they do not exist.

    This is idempotent and safe to run on each application startup.
    """
    # Create all tables defined in the ORM metadata.
    Base.metadata.create_all(bind=engine)
