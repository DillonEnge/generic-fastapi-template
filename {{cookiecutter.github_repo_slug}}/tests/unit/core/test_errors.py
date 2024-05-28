from data_api.core import errors


def test_internal_error_init() -> None:
    """Initialize an InternalError."""

    err = errors.InternalError(msg="test message")
    assert err.to_dict() == {
        "title": "Internal Server Error",
        "type": "about:blank",
        "status": 500,
        "detail": "test message",
    }


def test_user_error_init() -> None:
    """Initialize a UserError."""

    err = errors.UserError(msg="test message")
    assert err.to_dict() == {
        "title": "Bad Request",
        "type": "about:blank",
        "status": 400,
        "detail": "test message",
    }


def test_unauthorized_error_init() -> None:
    """Initialize an Unauthorized error.."""

    err = errors.Unauthorized(msg="test message")
    assert err.to_dict() == {
        "title": "Unauthorized",
        "type": "about:blank",
        "status": 401,
        "detail": "test message",
    }


def test_forbidden_error_init() -> None:
    """Initialize a Forbidden error.."""

    err = errors.Forbidden(msg="test message")
    assert err.to_dict() == {
        "title": "Forbidden",
        "type": "about:blank",
        "status": 403,
        "detail": "test message",
    }


def test_not_found_error_init() -> None:
    """Initialize a NotFound error.."""

    err = errors.NotFound(msg="test message")
    assert err.to_dict() == {
        "title": "Not Found",
        "type": "about:blank",
        "status": 404,
        "detail": "test message",
    }
