from asyncio import AbstractEventLoop

from data_api.core import events
from fastapi import FastAPI


def test_register_startup() -> None:
    """Register a startup event handler with an application."""
    app = FastAPI()

    # Verify there are no handlers registered.
    assert len(app.router.on_startup) == 0
    assert len(app.router.on_shutdown) == 0

    events.register_startup(app)

    # Now, there should be a single startup event handler.
    assert len(app.router.on_startup) == 1
    assert len(app.router.on_shutdown) == 0


def test_register_shutdown() -> None:
    """Register a shutdown event handler with an application."""
    app = FastAPI()

    # Verify there are no handlers registered.
    assert len(app.router.on_startup) == 0
    assert len(app.router.on_shutdown) == 0

    events.register_shutdown(app)

    # Now, there should be a single startup event handler.
    assert len(app.router.on_startup) == 0
    assert len(app.router.on_shutdown) == 1


def test_startup_shutdown_handler(event_loop: AbstractEventLoop) -> None:
    """The on_shutdown handler runs successfully."""
    app = FastAPI()
    events.register_startup(app)
    events.register_shutdown(app)

    startup_coro = app.router.on_startup[0]  # get the registered handler
    shutdown_coro = app.router.on_shutdown[0]  # get the registered handler

    # Run the startup handler
    event_loop.run_until_complete(startup_coro())

    # TODO: Verify any state change from the startup handler

    # Run the shutdown handler
    event_loop.run_until_complete(shutdown_coro())

    # TODO: Verify any state change from the shutdown handler
