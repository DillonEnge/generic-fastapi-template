"""Application metrics export for Prometheus."""

import time

from fastapi import FastAPI
from prometheus_client import Counter, Gauge, Histogram  # type: ignore
from prometheus_client.core import REGISTRY  # type: ignore
from prometheus_client.exposition import (  # type: ignore
    CONTENT_TYPE_LATEST,
    generate_latest,
)
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from ..utils import utils

HTTP_REQUESTS_TOTAL = Counter(
    name="http_requests_total",
    documentation="Total count of received HTTP requests",
    labelnames=("method", "path_template"),
)

HTTP_REQUESTS_LATENCY = Histogram(
    name="http_requests_latency_sec",
    documentation=(
        "Time it takes for HTTP requests to be completed (in seconds). This "
        "includes the time spent processing the middleware stack"
    ),
    labelnames=("method", "path_template"),
)

HTTP_REQUESTS_ACTIVE = Gauge(
    name="http_requests_active",
    documentation="Number of HTTP requests currently being processed",
    labelnames=("method", "path_template"),
)

HTTP_RESPONSES_TOTAL = Counter(
    name="http_responses_total",
    documentation="Total count of returned HTTP responses",
    labelnames=("method", "path_template", "status_code"),
)

HTTP_RESPONSES_BYTES = Counter(
    name="http_responses_bytes",
    documentation="Total count of bytes sent in HTTP response bodies",
    labelnames=("method", "path_template"),
)

HTTP_ERRORS_TOTAL = Counter(
    name="http_errors_total",
    documentation="Total count of errors raised when processing requests",
    labelnames=("method", "path_template", "error_type"),
)


def register(app: FastAPI) -> None:
    """Register the PrometheusMiddleware and metrics route with an application."""
    app.add_middleware(PrometheusMiddleware)
    app.add_route("/metrics", metrics)


def metrics(request: Request) -> Response:
    """Request handler for the route which serves Prometheus application metrics."""
    return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)


class PrometheusMiddleware:
    """Application middleware which collects application-level metrics on requests,
    responses, and errors.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope["method"]
        path_template = utils.get_request_route(scope)

        HTTP_REQUESTS_TOTAL.labels(method=method, path_template=path_template).inc()
        HTTP_REQUESTS_ACTIVE.labels(method=method, path_template=path_template).inc()

        before = time.perf_counter()

        async def send_wrapper(message: Message) -> None:
            message_type = message["type"]

            if message_type == "http.response.start":
                after = time.perf_counter()
                status_code = message["status"]

                HTTP_REQUESTS_LATENCY.labels(method=method, path_template=path_template).observe(
                    after - before
                )
                HTTP_RESPONSES_TOTAL.labels(
                    method=method, path_template=path_template, status_code=status_code
                ).inc()

            elif message_type == "http.response.body":
                body = message.get("body", b"")
                more_body = message.get("more_body", False)

                if not more_body:
                    # The response is complete - there is no more body data being streamed.
                    HTTP_RESPONSES_BYTES.labels(
                        method=method,
                        path_template=path_template,
                    ).inc(len(body))

            await send(message)  # pragma: nocover

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as exc:
            HTTP_ERRORS_TOTAL.labels(
                method=method,
                path_template=path_template,
                error_type=type(exc).__name__,
            ).inc()
            raise exc
        finally:
            HTTP_REQUESTS_ACTIVE.labels(method=method, path_template=path_template).dec()
