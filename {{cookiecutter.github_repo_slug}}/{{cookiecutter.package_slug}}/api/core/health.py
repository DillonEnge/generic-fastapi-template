"""Route to provide a high-level 'health' status for the application, intended
to be used for things like readiness and liveness probes.
"""

from typing import Dict

from fastapi import APIRouter

from ...metadata import tags
from ...schema.health import HealthStatus

router = APIRouter()


@router.get(
    path="/health",
    summary="Get a high-level health status for the application.",
    response_model=HealthStatus,
    tags=[tags.health],
)
async def get_application_health_status() -> Dict:
    """Get a high-level health status for the application."""

    return {"status": "ok"}
