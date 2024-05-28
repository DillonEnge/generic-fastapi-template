"""Functions used as hooks for the application/middleware."""

from containerlog import get_logger
from starlette.requests import Request

logger = get_logger()


def log_exc(req: Request, exc: Exception) -> None:
    """Hook for the rfc7807 middleware to log exceptions with context about the request.

    Args:
        req: The request which the Exception originated in.
        exc: The Exception instance itself.
    """
    logger.exception("exception occurred while processing request", req=req)
