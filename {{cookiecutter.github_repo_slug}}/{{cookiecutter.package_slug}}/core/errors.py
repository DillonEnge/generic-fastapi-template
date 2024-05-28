"""Custom error definitions for the Data API application."""

from fastapi_rfc7807.middleware import Problem


class APIError(Problem):
    """Base error class for all custom application error definitions.

    This class should be used as the base class for any custom errors as it allows
    for generalized exception handling for API errors.
    """


class InternalError(APIError):
    """Base error class for any unexpected or general-case error which occurs
    while processing a request.

    This returns an error response with HTTP 500 status code.
    """

    def __init__(self, msg: str) -> None:
        super(InternalError, self).__init__(
            title="",
            status=500,
            detail=msg,
        )


class UserError(APIError):
    """The user provided invalid or unexpected data.

    This returns an error response with HTTP 400 status code.
    """

    def __init__(self, msg: str) -> None:
        super(UserError, self).__init__(
            title="",
            status=400,
            detail=msg,
        )


class Unauthorized(APIError):
    """User authorization failed.

    This returns an error response with HTTP 401 status code.
    """

    def __init__(self, msg: str) -> None:
        super(Unauthorized, self).__init__(
            title="",
            status=401,
            detail=msg,
        )


class Forbidden(APIError):
    """The user is not allowed to access the resource.

    This returns an error response with HTTP 403 status code.
    """

    def __init__(self, msg: str) -> None:
        super(Forbidden, self).__init__(
            title="",
            status=403,
            detail=msg,
        )


class NotFound(APIError):
    """A given resource is not found.

    This returns an error response with HTTP 404 status code.
    """

    def __init__(self, msg: str) -> None:
        super(NotFound, self).__init__(
            title="",
            status=404,
            detail=msg,
        )
