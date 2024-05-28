"""Definitions of well-known sharable `responses` metadata for API routes.

This metadata is used in the route decorator under the `responses` key to provide
additional details about the different response schemas with various status codes.

Not all routes need to use these metadata, however it is a useful place to put
common definitions to prevent repetition and make the codebase more maintainable.
"""

from typing import Any, Dict, Mapping, Union

from ..core.typing import BasicDict

__all__ = (
    "response_400",
    "response_401",
    "response_403",
    "response_404",
    "response_500",
    "common",
)


response_400 = {
    400: {
        "description": "Bad Request (invalid user input)",
        "content": {
            "application/problem+json": {
                "example": {
                    "type": "about:blank",
                    "title": "Bad Request",
                    "status": 400,
                    "detail": "Failed to load JSON payload",
                },
                "schema": {
                    "$ref": "#/components/schemas/Problem",
                },
            }
        },
    }
}


response_401 = {
    401: {
        "description": "Unauthorized (failed to authenticate)",
        "content": {
            "application/problem+json": {
                "example": {
                    "type": "about:blank",
                    "title": "Unauthorized",
                    "status": 401,
                    "detail": "Authorization header not provided in request headers",
                },
                "schema": {
                    "$ref": "#/components/schemas/Problem",
                },
            }
        },
    }
}

response_403 = {
    403: {
        "description": "Forbidden (unauthorized action)",
        "content": {
            "application/problem+json": {
                "example": {
                    "type": "about:blank",
                    "title": "Forbidden",
                    "status": 403,
                    "detail": "User does not have sufficient permissions",
                },
                "schema": {
                    "$ref": "#/components/schemas/Problem",
                },
            }
        },
    }
}

response_404 = {
    404: {
        "description": "Not Found (resource not found)",
        "content": {
            "application/problem+json": {
                "example": {
                    "type": "about:blank",
                    "title": "Not Found",
                    "status": 404,
                    "detail": "Resource not found",
                },
                "schema": {
                    "$ref": "#/components/schemas/Problem",
                },
            }
        },
    }
}

response_500 = {
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/problem+json": {
                "example": {
                    "exc_type": "ValueError",
                    "type": "about:blank",
                    "title": "Unexpected Server Error",
                    "status": 500,
                    "detail": "An unexpected error occurred",
                },
                "schema": {
                    "$ref": "#/components/schemas/Problem",
                },
            }
        },
    }
}

_codes_mapping: Mapping[int, Any] = {
    400: response_400,
    401: response_401,
    403: response_403,
    404: response_404,
    500: response_500,
}


def common(*statuses: int) -> Mapping[Union[int, str], BasicDict]:
    """Get a collection of common metadata responses.

    This is a convenience method so routes which require multiple status codes can,
    instead of declaring them individually:

        @router.post(
            ...
            responses={
                **responses.response_401,
                **responses.response_403,
                **responses.response_404,
                **responses.response_500,
            }
        )

    they can aggregate them with this method:

        @router.post(
            ...
            responses={
                **responses.common(401, 403, 404, 500),
            }
        )

    Args:
        statuses: The status codes for the desired common responses.
    """

    final: Dict[Union[int, str], BasicDict] = {}
    for status in statuses:
        resp = _codes_mapping.get(status)
        if resp is None:
            raise RuntimeError(f"Unsupported common metadata response status specified ({status})")
        final.update(resp)
    return final
