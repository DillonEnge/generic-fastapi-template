"""Models for Health status responses."""

from pydantic import BaseModel


class HealthStatus(BaseModel):
    """A representation of the application's health status."""

    status: str = "ok"
