from typing import Generator

from ..db.session import SessionLocal


def get_db() -> Generator:
    """Get a new database session.

    This is intended to be used as a FastAPI Dependency for a single request.
    Once the request completes, the database session is closed.
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
