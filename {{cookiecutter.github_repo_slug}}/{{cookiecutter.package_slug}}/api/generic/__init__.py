"""Data API v1 root router definition.

The router defined here should be used by all v1 API route declarations.
This is done as a convenience so it is easier to register all v1 routes
with the FastAPI application.
"""
from fastapi import APIRouter

from . import generic_routes

__all__ = ["router"]

v1_prefix = "/v1"

router = APIRouter()

router.include_router(generic_routes.router, prefix=v1_prefix)
