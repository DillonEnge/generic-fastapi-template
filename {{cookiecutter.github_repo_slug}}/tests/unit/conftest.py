import containerlog
import pytest
from data_api.main import get_application
from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient
from sqlalchemy import create_engine  # type: ignore
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker  # type: ignore
from starlette.types import Scope


@pytest.fixture(autouse=True)
def disable_logger() -> None:
    """Disable the application logger for unit tests.

    This helps to keep the test output cleaner and more easily readable. If there are
    cases where having the extra logging would be helpful, simply disable this fixture.
    """

    containerlog.disable()


@pytest.fixture(scope="session")
def test_app() -> FastAPI:
    """Create an instance of a FastAPI app for Data API test cases."""

    app = get_application()

    return app


@pytest.fixture()
def test_client(test_app) -> TestClient:
    """Create a FastAPI test client."""

    return TestClient(
        app=test_app,
        raise_server_exceptions=False,
    )


@pytest.fixture()
def request_scope(test_app) -> Scope:
    """Get a basic instance of a Starlette request scope."""

    return {
        "type": "http",
        "method": "get",
        "app": test_app,
        "root_path": "",
        "path": "/",
        "raw_path": b"/",
        "headers": {},
    }


@pytest.fixture()
def http_request(request_scope) -> Request:
    """Get a basic instance of a FastAPI request."""

    return Request(scope=request_scope)


@pytest.fixture()
def http_response() -> Response:
    """Get a basic instance of a FastAPI response."""

    return Response()


@pytest.fixture(scope="session")
def db_engine() -> Engine:
    """Generate an SQLAlchemy in-memory engine which is cleaned up after the test session."""

    engine = create_engine("sqlite://")
    yield
    engine.dispose()


@pytest.fixture(scope="session")
def db_session_factory(db_engine) -> scoped_session:
    """Get a scopes SQLAlchemy session factory."""

    return scoped_session(sessionmaker(bind=db_engine))


@pytest.fixture(scope="function")
def db_session(db_session_factory) -> Session:
    """Get an SQLAlchemy session which is rolled back and closed after the test."""

    session = db_session_factory()
    yield session
    session.rollback()
    session.close()
