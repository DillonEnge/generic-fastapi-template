from typing import Any, Dict, List, Optional

from fastapi.responses import Response


def check_ok_response_headers(
    resp: Response, contains: Optional[List[str]] = None, equals: Optional[Dict[str, str]] = None
) -> None:
    """Check headers for a response which returned without error.

    This helper includes some built-in checks for well-known headers
    which should always be associated with an ok response.

    Args:
        resp: The Response to check headers for.
        contains: Header keys to verify are contained within the response
            headers, but without any checking against their values.
        equals: Header keys mapped to expected values. Check that these are
            contained in the response headers and that the values matches
            those provided here.
    """
    expected_in = []
    expected_eq = {
        "content-type": "application/json",
    }

    if contains:
        expected_in.extend(contains)
    if equals:
        expected_eq.update(equals)

    check_response_headers(resp=resp, contains=expected_in, equals=expected_eq)


def check_err_response_headers(
    resp: Response, contains: Optional[List[str]] = None, equals: Optional[Dict[str, str]] = None
) -> None:
    """Check headers for a response which returned with error.

    This helper includes some built-in checks for well-known headers
    which should always be associated with an error response.

    Args:
        resp: The Response to check headers for.
        contains: Header keys to verify are contained within the response
            headers, but without any checking against their values.
        equals: Header keys mapped to expected values. Check that these are
            contained in the response headers and that the values matches
            those provided here.
    """
    expected_in = []
    expected_eq = {
        "content-type": "application/problem+json",
    }

    if contains:
        expected_in.extend(contains)
    if equals:
        expected_eq.update(equals)

    check_response_headers(resp=resp, contains=expected_in, equals=expected_eq)


def check_response_headers(
    resp: Response, contains: Optional[List[str]] = None, equals: Optional[Dict[str, str]] = None
) -> None:
    """Check that a response has all of the specified headers.

    Args:
        resp: The Response to check headers for.
        contains: Header keys to verify are contained within the response
            headers, but without any checking against their values.
        equals: Header keys mapped to expected values. Check that these are
            contained in the response headers and that the values matches
            those provided here.
    """
    for header in contains:
        assert header in resp.headers, f"{header} not in response headers"

    for k, v in equals.items():
        assert k in resp.headers, f"{k} not in response headers"
        assert v == resp.headers[k], f"{v} does not match response header {resp.headers[k]}"


def err500(msg: str, exc_type=None, title=None) -> Dict[str, Any]:
    """Get a dictionary modeling a 500 error response with the given message.

    Args:
        msg: The message string found in the "detail" field.
        exc_type: The type of Exception expected to be surfaced.
        title: A value for the "title" field, if different from the default
            "Unexpected Server Error".

    Returns:
        The expected error JSON as a dictionary.
    """
    err = {
        "detail": msg,
        "status": 500,
        "title": "Unexpected Server Error",
        "type": "about:blank",
    }
    if exc_type:
        err["exc_type"] = exc_type
    if title:
        err["title"] = title

    return err


def err400(msg: str, title=None, errors=None) -> Dict[str, Any]:
    """Get a dictionary modeling a 400 error response with the given message.

    Args:
        msg: The message string found in the "detail" field.
        title: A value for the "title" field, if different from the default
            "Validation Error".
        errors: A collection of errors which may be associated with the message
            (e.g. if it is a validation error).

    Returns:
        The expected error JSON as a dictionary.
    """
    err = {
        "detail": msg,
        "status": 400,
        "title": "Validation Error",
        "type": "about:blank",
    }
    if title:
        err["title"] = title
    if errors:
        err["errors"] = errors
    return err


def err401(msg: str) -> Dict[str, Any]:
    """Get a dictionary modeling a 401 error response with the given message.

    Args:
        msg: The message string found in the "detail" field.

    Returns:
        The expected error JSON as a dictionary.
    """
    return {
        "detail": msg,
        "status": 401,
        "title": "Unauthorized",
        "type": "about:blank",
    }


def err403(msg: str) -> Dict[str, Any]:
    """Get a dictionary modeling a 403 error response with the given message.

    Args:
        msg: The message string found in the "detail" field.

    Returns:
        The expected error JSON as a dictionary.
    """
    return {
        "detail": msg,
        "status": 403,
        "title": "Forbidden",
        "type": "about:blank",
    }


def err404(msg: str) -> Dict[str, Any]:
    """Get a dictionary modeling a 404 error response with the given message.

    Args:
        msg: The message string found in the "detail" field.

    Returns:
        The expected error JSON as a dictionary.
    """
    return {
        "detail": msg,
        "status": 404,
        "title": "Not Found",
        "type": "about:blank",
    }
