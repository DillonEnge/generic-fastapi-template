"""Global database engine and session factory."""

from sqlalchemy import MetaData, create_engine  # type: ignore
from sqlalchemy.orm import sessionmaker  # type: ignore

from ..core.config import settings

engine = create_engine(
    settings.sqlalchemy_database_uri,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

metadata = MetaData()
