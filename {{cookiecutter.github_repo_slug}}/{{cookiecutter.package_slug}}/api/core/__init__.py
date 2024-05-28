"""Data API core (un-versioned) root router definition.

The router defined here should be used by all un-versioned API route declarations.
This is done as a convenience so it is easier to register all core routes
with the FastAPI application.
"""

from fastapi import APIRouter

from . import health

__all__ = ["router"]

# The core router holds all of the API routes defined in the data_api.api.core
# package. If additional routes are added, be sure to include them here.
router = APIRouter()

router.include_router(health.router)
