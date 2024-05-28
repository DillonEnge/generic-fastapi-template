import pytest


@pytest.fixture(scope="session")
def err405_json():
    """Get the expected error message for requests resulting in 405 responses."""
    return {
        "type": "about:blank",
        "title": "Method Not Allowed",
        "status": 405,
        "detail": "Method Not Allowed",
    }
