import pytest
import testutils  # tests/unit/testutils.py
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    "method",
    (
        "options",
        "head",
        "put",
        "post",
        "patch",
        "delete",
    ),
)
def test_health_route_not_allowed(test_client: TestClient, err405_json: dict, method: str) -> None:
    """Verify that requests with unsupported HTTP methods for the /health
    route return a 405 error.
    """

    resp = getattr(test_client, method)("/health")
    assert resp.status_code == 405
    assert resp.headers.get("content-type") == "application/problem+json"
    if method != "head":
        assert resp.json() == err405_json


class TestGetApplicationHealthStatus:
    def test_ok(self, test_client: TestClient) -> None:
        """Successfully get application health status."""

        response = test_client.get("/health")
        assert response.status_code == 200
        assert response.json() == {
            "status": "ok",
        }
        testutils.check_ok_response_headers(response)
