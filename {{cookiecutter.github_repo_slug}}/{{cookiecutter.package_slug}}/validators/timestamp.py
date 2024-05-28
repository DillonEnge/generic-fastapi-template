"""Custom pydantic validator for RFC3339 timestamp strings."""

import re
from typing import Any, Dict, Generator, Union

from pydantic.networks import str_validator
from pydantic.typing import AnyCallable

CallableGenerator = Generator[AnyCallable, None, None]

# https://stackoverflow.com/a/48881514
rfc3339_regex = r"^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$"  # noqa
_match = re.compile(rfc3339_regex).match


class RFC3339Timestamp(str):
    """Validator class for ensuring strings are valid RFC3339 timestamps.

    The implementation of this class is based on custom pydantic validator
    types, as implemented in the pydantic.networks module.

    See RFC 3339 (ISO 8601) for details on the format.
    https://www.ietf.org/rfc/rfc3339.txt
    """

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(type="string", format="date-time")  # pragma: nocover

    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        yield str_validator
        yield cls.validate

    @classmethod
    def validate(cls, value: Union[str]) -> str:
        return validate_rfc3339(value)


def validate_rfc3339(timestamp: Union[str]) -> str:
    """Ensure the string is an RFC3339 (ISO 8601) formatted timestamp.

    Because of the different valid formats an RFC3339 timestamp can take,
    particularly around timezone formatting, this check is done by matching
    the input string against a regex.

    Args:
        timestamp: The string to validate.

    Returns:
        The input string, if it is a valid timestamp.

    Raises:
        ValueError: The input string is not a valid RFC3339 timestamp.
    """
    try:
        if _match(timestamp) is not None:
            return timestamp
        msg = "input string did not match timestamp regex"
    except Exception as exc:
        msg = str(exc)

    raise ValueError(f"invalid rfc3339 timestamp: {msg}")
