import pytest
from data_api.metadata import responses


@pytest.mark.parametrize(
    "code",
    [
        400,
        401,
        403,
        404,
        500,
    ],
)
def test_common_single(code: int) -> None:
    """Test aggregating metadata responses for a single status code."""

    result = responses.common(code)

    assert len(result) == 1
    assert code in result
    assert "description" in result[code]
    assert "content" in result[code]


def test_common_multiple() -> None:
    """Test aggregating metadata responses for multiple status codes."""

    result = responses.common(400, 404, 500)

    assert len(result) == 3
    assert 400 in result
    assert 404 in result
    assert 500 in result


def test_common_no_code() -> None:
    """Provide a code which does not have a metadata template."""

    with pytest.raises(RuntimeError):
        responses.common(555)


def test_common_no_code_in_multiple() -> None:
    """Provide a code among multiple which does not have a metadata template."""

    with pytest.raises(RuntimeError):
        responses.common(400, 404, 555)
