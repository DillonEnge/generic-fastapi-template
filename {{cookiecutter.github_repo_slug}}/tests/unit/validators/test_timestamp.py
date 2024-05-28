import pytest
from data_api.validators.timestamp import RFC3339Timestamp, validate_rfc3339
from pydantic import BaseModel, ValidationError


def test_rfc339_timestamp_valid() -> None:
    """The validator class successfully validates a proper RFC3339 timestamp."""

    class Model(BaseModel):
        v: RFC3339Timestamp

    assert (
        Model(v=RFC3339Timestamp("2017-04-13T14:34:23.111142+00:00")).v
        == "2017-04-13T14:34:23.111142+00:00"
    )
    assert Model(v="2017-04-13T14:34:23.111142+00:00").v == "2017-04-13T14:34:23.111142+00:00"


def test_rfc339_timestamp_invalid() -> None:
    """The validator class fails to validate an invalid RFC3339 timestamp."""

    class Model(BaseModel):
        v: RFC3339Timestamp

    with pytest.raises(ValidationError):
        Model(v=RFC3339Timestamp("2020-01-01"))

    with pytest.raises(ValidationError):
        Model(v="2020-01-01")


@pytest.mark.parametrize(
    "value",
    [
        "2008-08-30T01:45:36",
        "2008-08-30T01:45:36.123Z",
        "2017-04-13T14:34:23.111142+00:00",
        "2017-04-13T14:34:23.111142Z",
        "2016-12-13T21:20:37.593194+05:00",
        "2016-12-13T21:20:37.593194-05:00",
    ],
)
def test_validate_rfc3339_valid(value: str) -> None:
    """The input string is a valid RFC3339-formatted timestamp."""

    assert validate_rfc3339(value) == value


@pytest.mark.parametrize(
    "value",
    [
        None,
        "",
        "foobar",
        "123",
        "2020-01-01",
        "January 1 2020",
        "2016-12-13 T 21:20:37.593194-05:00",
        "2016-12-13T21:20:37.593194~05:00",
        "2016-12-13T21:20:37.593194+0500",
        "2017-04-13T14:34:23.111142Q",
    ],
)
def test_validate_rfc3339_invalid(value: str) -> None:
    """The input string is not a valid RFC3339-formatted timestamp."""

    with pytest.raises(ValueError):
        validate_rfc3339(value)
