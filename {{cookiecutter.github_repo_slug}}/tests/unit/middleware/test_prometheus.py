from unittest import mock

import pytest
from data_api.middleware import prometheus
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from starlette.types import ASGIApp, Receive, Scope, Send


def test_register(basic_app: FastAPI) -> None:
    """The middleware successfully registers to the app."""

    assert len(basic_app.user_middleware) == 0
    prometheus.register(basic_app)
    assert len(basic_app.user_middleware) == 1
    assert "metrics" in [r.name for r in basic_app.router.routes]


def test_metrics(http_request: Request) -> None:
    """The metrics route handler successfully returns metrics."""

    resp = prometheus.metrics(http_request)
    # A pretty "dumb" assertion that does not capture all the possible detail
    # and nuance possible, but it basically just verifies that the output response
    # is the expected Prometheus-scrapable text.
    assert b"python_gc_objects_collected_total" in resp.body


class TestPrometheusMiddleware:
    @mock.patch("prometheus_client.Counter.inc")
    @mock.patch("prometheus_client.Gauge.inc")
    @mock.patch("prometheus_client.Histogram.observe")
    def test_collects_metrics_http(
        self, mock_hist, mock_gauge, mock_counter, basic_app: FastAPI
    ) -> None:
        """The middleware processes and generates metrics."""

        basic_app.add_middleware(prometheus.PrometheusMiddleware)
        client = TestClient(basic_app)

        resp = client.get("/simple")
        assert resp.status_code == 200

        mock_hist.assert_called_once()  # requests latency
        mock_gauge.assert_called_once()  # requests active
        mock_counter.assert_has_calls(
            [
                mock.call(),  # requests total
                mock.call(),  # responses total
                mock.call(13),  # response bytes
            ]
        )

    @mock.patch("prometheus_client.Counter.inc")
    @mock.patch("prometheus_client.Gauge.inc")
    @mock.patch("prometheus_client.Histogram.observe")
    def test_collects_metrics_http_stream(
        self, mock_hist, mock_gauge, mock_counter, basic_app: FastAPI
    ) -> None:
        """The middleware processes and generates metrics."""

        basic_app.add_middleware(prometheus.PrometheusMiddleware)
        client = TestClient(basic_app)

        resp = client.get("/stream")
        assert resp.status_code == 200

        mock_hist.assert_called_once()  # requests latency
        mock_gauge.assert_called_once()  # requests active
        mock_counter.assert_has_calls(
            [
                mock.call(),  # requests total
                mock.call(),  # responses total
                mock.call(0),  # response bytes - 0 because we can't aggregate on a stream yet
            ]
        )

    @mock.patch("prometheus_client.Counter.inc")
    @pytest.mark.asyncio
    async def test_middleware_not_http_scope(self, mock_counter, basic_app: FastAPI):
        """The middleware passes through if the request is not an HTTP request."""
        basic_app.add_middleware(prometheus.PrometheusMiddleware)
        client = TestClient(basic_app)

        with client.websocket_connect("/ws") as websocket:
            # Issue some calls over the websocket so the middleware stack gets called.
            websocket.send_text("testing")
            websocket.receive_text()

            # Ensure that the prometheus middleware passed through and did not actually
            # run. We can check this by verifying that no Counters were incremented.
            assert mock_counter.not_called()

    @mock.patch("prometheus_client.Counter.inc")
    @mock.patch("prometheus_client.Gauge.inc")
    @mock.patch("prometheus_client.Histogram.observe")
    def test_collects_metrics_error(
        self, mock_hist, mock_gauge, mock_counter, basic_app: FastAPI
    ) -> None:
        """The middleware processes and generates metrics."""

        class ErrorMiddleware:
            """Middleware that errors."""

            def __init__(self, app: ASGIApp) -> None:
                self.app = app

            async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
                raise ValueError("test")

        basic_app.add_middleware(ErrorMiddleware)
        basic_app.add_middleware(prometheus.PrometheusMiddleware)
        client = TestClient(basic_app)

        with pytest.raises(ValueError):
            client.get("/simple")

        mock_hist.assert_not_called()  # requests latency
        mock_gauge.assert_called_once()  # requests active
        mock_counter.assert_has_calls(
            [
                mock.call(),  # requests total
                mock.call(),  # errors total
            ]
        )
