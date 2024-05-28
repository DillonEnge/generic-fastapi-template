"""General application utility functions."""
import json
from datetime import datetime
from typing import Any, Dict, List
from uuid import UUID

from containerlog import get_logger
from pydantic import BaseConfig, create_model
from pydantic.config import Extra
from sqlalchemy import and_, or_, select  # type: ignore
from sqlalchemy.engine import Row  # type: ignore
from sqlalchemy.sql.elements import TextClause  # type: ignore
from starlette.routing import Match
from starlette.types import Scope

from ..core.config import settings
from ..db.session import SessionLocal, metadata
from ..validators.timestamp import RFC3339Timestamp

logger = get_logger()

__all__ = [
    "get_request_route",
    "dict_from_row",
    "get_schema_models",
    "table_from_name",
    "generate_custom_openapi_paths",
    "generate_custom_openapi_schemas",
    "generate_custom_openapi_tags",
]


def get_request_route(scope: Scope) -> str:
    """Get the name of the request route or route template.

    Args:
        scope: The request scope to get the route name/template from.

    Returns:
        The name/template for the request.
    """
    url_path = scope.get("root_path", "") + scope["path"]
    app = scope.get("app")
    if app:
        for route in app.routes:
            match, _ = route.matches(scope)
            if match == Match.FULL:
                return route.path
    return url_path


def dict_from_row(row: Row) -> Dict:
    """Create a dict with proper datetime ISO format from a sqlalchemy row object.

    Args:
        row: The sqlalchemy returned row object to be converted to a dict.

    Returns:
        The new properly formatted dict.
    """
    built_obj = {}

    for key in row._fields:
        if isinstance(row[key], datetime):
            built_obj[key] = row[key].isoformat(sep="T")
        else:
            built_obj[key] = row[key]

    return built_obj


def snake_to_camel(text: str):
    """Convert a snake cased string to a camel cased string.

    Args:
        text: The snake cased text to be converted.

    Returns:
        The camel cased version of the string.
    """
    return "".join([word.title() for word in text.split("_")])


def table_from_name(table_name: str):
    """Get a table object from a table name.

    Args:
        table_name: The table name to fetch a table with.

    Returns:
        The fetched table.
    """
    return metadata.tables.get(table_name)


def get_schema_models(table_name: str):
    """Get schema models for custom openapi generation.

    Args:
        table_name: The table name to generate schema models from.

    Returns:
        The generated schema models.
    """
    if settings.suppress_abstract_table_docs:
        if table_name in ["relationships", "operations"]:
            return {}

    db = SessionLocal()

    operations = executioner.get_operations(table_name, db)

    if table_name not in ["relationships", "operations"] and operations == {}:
        return {}

    db.close()

    return_fields = {}
    payload_fields = {}
    opt_payload_fields = {}

    table = table_from_name(table_name)

    table_name_camel = snake_to_camel(table_name)

    if table == None:
        return {}

    relationships = []

    with SessionLocal() as db:
        relationships_table = table_from_name("relationships")

        stmt = select(relationships_table).where(
            or_(
                relationships_table.c.primary_table_name == table_name,
                and_(
                    relationships_table.c.secondary_table_name == table_name,
                    relationships_table.c.associative_table_name != None,
                ),
            ),
        )

        results = db.execute(stmt).fetchall()

        relationships = [dict_from_row(result) for result in results]

    for col in table.c:
        col_name = str(col.name)

        return_fields[col_name] = (python_type_from_col(col), default_from_col(col))

        if col_name not in ["id", "created_at", "updated_at", "deleted_at"]:
            payload_fields[col_name] = (python_type_from_col(col), default_from_col(col))
            opt_payload_fields[col_name] = (python_type_from_col(col), None)

    for relationship in relationships:
        relationship_name = relationship["secondary_table_name"]

        if relationship_name == table_name:
            relationship_name = relationship["primary_table_name"]

        is_many_to_many = relationship["associative_table_name"] is not None

        relationship_type = (List[UUID], [])  # type: ignore

        return_fields[relationship_name] = relationship_type  # type: ignore

        if is_many_to_many:
            payload_fields[relationship_name] = relationship_type  # type: ignore
            opt_payload_fields[relationship_name] = relationship_type  # type: ignore

    class Config(BaseConfig):
        extra = Extra("forbid")

    model_return = create_model(f"{table_name_camel}Return", **return_fields)  # type: ignore
    model_payload = create_model(
        f"{table_name_camel}Payload",
        **payload_fields,
        __config__=Config,
    )  # type: ignore
    model_opt_payload = create_model(
        f"{table_name_camel}OptPayload",
        **opt_payload_fields,
        __config__=Config,
    )  # type: ignore

    return {
        "ModelReturn": model_return,
        "ModelPayload": model_payload,
        "ModelOptPayload": model_opt_payload,
    }


def default_from_col(col: Any):
    """Get the server default value from a column.

    Args:
        col: The column to derive the default from.

    Returns:
        The proper default value for the column.
    """
    default = col.server_default

    if default:
        if isinstance(default.arg, TextClause):
            if str(default.arg).find("()") != -1:
                return ...

            if str(default.arg) in ["true", "false"]:
                return eval(str(default.arg).capitalize())

        return default.arg
    else:
        if col.nullable:
            return None

        return ...


def python_type_from_col(col: Any):
    """Get the python type from a column.

    Args:
        col: The column to derive the python type from.

    Returns:
        The proper python type from the column.
    """
    if col.name == "id":
        return UUID
    elif col.type.python_type == datetime:
        return RFC3339Timestamp

    return col.type.python_type


def generate_custom_openapi_paths():
    """Generate custom openapi paths for use in generation.

    Returns:
        The custom openapi paths.
    """
    new_paths = {}
    for table_name in metadata.tables.keys():
        for path, definition in get_paths(table_name).items():
            new_paths[path] = definition

    return new_paths


def generate_custom_openapi_schemas():
    """Generate custom openapi schemas for use in generation.

    Returns:
        The custom openapi schemas.
    """
    new_schemas = {}
    for table_name in metadata.tables.keys():
        for schema_name, definition in get_schemas(table_name).items():
            new_schemas[schema_name] = definition

    return new_schemas


def generate_custom_openapi_tags():
    """Generate custom openapi tags for use in generation.

    Returns:
        The custom openapi tags.
    """
    new_tags = []

    with open("dev/tags.json") as f:
        tag_json = json.load(f)

    for table_name in metadata.tables.keys():
        table_name_camel = snake_to_camel(table_name)

        if table_name in tag_json.keys():
            new_tags.append({
                "name": table_name_camel,
                "description": tag_json[table_name],
            })

    return new_tags


def split_rtrim(text: str, delimiter: str):
    """Split and trim the right of a string.

    Args:
        text: The text to perform operations on.
        delimiter: The string to delimit the text split.

    Returns:
        The split and trimmed array from the provided string.
    """
    split_text = text.split(delimiter)

    if split_text[-1] == "":
        split_text.pop()

    return split_text


from ..db.exc import executioner # noqa: E402
from ..docs.utils import get_paths, get_schemas  # noqa: E402
