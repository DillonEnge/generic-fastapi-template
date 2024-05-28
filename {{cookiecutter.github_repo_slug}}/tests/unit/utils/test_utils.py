from data_api.utils import utils
from starlette.types import Scope


def test_get_request_route_basic(request_scope: Scope) -> None:
    """Get the route for a basic, normal request."""

    request_scope["path"] = "/v1/route"
    request_scope["raw_path"] = b"/v1/route"

    route = utils.get_request_route(request_scope)
    assert route == "/v1/route"


def test_get_request_route_not_found(request_scope: Scope) -> None:
    """Get the route for something the app does not define."""

    request_scope["path"] = "/foobar"
    request_scope["raw_path"] = b"/foobar"

    route = utils.get_request_route(request_scope)
    assert route == "/foobar"


def test_get_request_route_no_app(request_scope: Scope) -> None:
    """Get the route for a basic, normal request."""

    del request_scope["app"]
    request_scope["path"] = "/v1/route"
    request_scope["raw_path"] = b"/v1/route"

    route = utils.get_request_route(request_scope)
    assert route == "/v1/route"
