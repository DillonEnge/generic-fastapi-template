from data_api import main


def test_get_application() -> None:
    """Get a new instance of the Vator application successfully."""

    app = main.get_application()
    assert app.title == "Data API"
