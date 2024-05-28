"""Declarative base class for DB ORM models.

All ORM models are required to inherit from this base class.
"""

import re
from typing import Any

from sqlalchemy.ext.declarative import as_declarative, declared_attr  # type: ignore


@as_declarative()
class Base:
    """Base class for all SQLAlchemy ORM models."""

    id: Any
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        """Automatically generate the table name from the class name.

        This will transform the class name from PascalCase to snake_case and will
        ensure it is all lower-cased. For example:

            class Users:
                ...

        would have the table name 'users'.

            class UserInfo:
                ...

        would have the table name 'user_info'.
        """
        return re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()
