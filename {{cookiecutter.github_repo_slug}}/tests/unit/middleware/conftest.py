import pytest
from fastapi import FastAPI, Request, Response, WebSocket
from fastapi.responses import JSONResponse, StreamingResponse


@pytest.fixture()
def basic_app() -> FastAPI:
    """Get a basic FastAPI app with single route configured.

    This is intended to be used for testing application middleware.
    """
    app = FastAPI()

    @app.route("/")
    async def index(request: Request) -> Response:
        return Response(status_code=204)

    @app.route("/simple")
    async def simple(request: Request) -> JSONResponse:
        return JSONResponse({"foo": "bar"}, status_code=200)

    @app.route("/stream")
    async def stream(request: Request) -> StreamingResponse:
        async def streamer():
            for i in range(5):
                yield f"data-{i}"

        return StreamingResponse(streamer())

    @app.websocket("/ws")
    async def websocket_route(ws: WebSocket):
        await ws.accept()
        data = await ws.receive_text()
        await ws.send_text(f"response for: {data}")

    return app
