"""Application configuration management.

For details, see: https://pydantic-docs.helpmanual.io/usage/settings/
"""
from typing import Any, Dict, Optional

from pydantic import BaseSettings, PostgresDsn, validator


class Settings(BaseSettings):
    """Configuration settings for Data API."""

    # Run the application with debug logging.
    debug: bool = False

    # Suppress the abstract tables (relationships, operations) from docs.
    suppress_abstract_table_docs: bool = False

    # Configuration options for the connection to the Postgres server.
    postgres_host: str
    postgres_port: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    sqlalchemy_database_uri: Optional[PostgresDsn] = None

    @validator("sqlalchemy_database_uri", pre=True)
    def assemble_postgres_dsn(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v

        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("postgres_user"),
            password=values.get("postgres_password"),
            host=values.get("postgres_host"),
            port=values.get("postgres_port"),
            path=f"/{values.get('postgres_db') or ''}",
        )

    class Config:
        env_prefix = "APP_"


# Create a global instance of the configuration settings, loaded at
# application startup (e.g. on import).
settings: Settings = Settings()
