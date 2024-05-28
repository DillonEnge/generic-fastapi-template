"""Event handlers for application startup/shutdown."""

from containerlog import get_logger
from fastapi import FastAPI

logger = get_logger()


def register_startup(app: FastAPI) -> None:
    """Register a startup event handler for the application.

    Args:
        app: The application to register the startup event to.
    """

    async def on_startup():
        """Event handler for application startup."""
        logger.info("application startup")

        # TODO: Add any application startup code here.
        #   The application state may be used to cache things for application-wide access, e.g.
        #
        #       app.state.something = 'foobar'

    app.add_event_handler("startup", on_startup)


def register_shutdown(app: FastAPI) -> None:
    """Register a shutdown event handler for the application.

    Args:
        app: The application to register the shutdown event to.
    """

    async def on_shutdown():
        """Event handler for application shutdown."""
        logger.info("application shutdown")

        # TODO: Add any application shutdown code here.

    app.add_event_handler("shutdown", on_shutdown)
