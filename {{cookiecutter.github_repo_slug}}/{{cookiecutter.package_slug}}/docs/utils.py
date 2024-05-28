from ..core.config import settings
from ..db.exc import executioner
from ..db.session import SessionLocal
from ..utils.utils import get_schema_models, snake_to_camel

__all__ = [
    "get_paths",
    "get_schemas",
]

problem_schema = {
    "title": "Problem",
    "description": "Model of the RFC7807 Problem response schema.",
    "type": "object",
    "properties": {
        "type": {
            "title": "Type",
            "type": "string",
        },
        "title": {
            "title": "Title",
            "type": "string",
        },
        "status": {
            "title": "Status",
            "type": "integer",
        },
        "detail": {
            "title": "Detail",
            "type": "string",
        },
        "instance": {
            "title": "Instance",
            "type": "string",
        },
    },
    "required": [
        "type",
        "title",
    ],
}

error_responses = {
    "401": {
        "description": "Unauthorized (failed to authenticate)",
        "content": {
            "application/problem+json": {
                "schema": {
                    "$ref": "#/components/schemas/Problem",
                },
                "example": {
                    "type": "about:blank",
                    "title": "Unauthorized",
                    "status": 401,
                    "detail": "Authorization header not provided in request headers",
                },
            },
        },
    },
    "403": {
        "description": "Forbidden (unauthorized action)",
        "content": {
            "application/problem+json": {
                "schema": {
                    "$ref": "#/components/schemas/Problem",
                },
                "example": {
                    "type": "about:blank",
                    "title": "Forbidden",
                    "status": 403,
                    "detail": "User does not have sufficient permissions",
                },
            },
        },
    },
    "422": {
        "description": "Validation Error",
        "content": {
            "application/json": {
                "schema": {
                    "$ref": "#/components/schemas/HTTPValidationError",
                },
            },
        },
    },
    "500": {
        "description": "Internal Server Error",
        "content": {
            "application/problem+json": {
                "schema": {
                    "$ref": "#/components/schemas/Problem",
                },
                "example": {
                    "exc_type": "ValueError",
                    "type": "about:blank",
                    "title": "Unexpected Server Error",
                    "status": 500,
                    "detail": "An unexpected error occurred",
                },
            },
        },
    },
}


def build_responses(table_name: str, list_response: bool = False):
    """Build all appropriate status_code responses.

    Args:
        table_name: The table name to build responses for.
        list_response: A bool indicating if this response should be a list.

    Returns:
        The newly created responses.
    """
    table_name_camel = snake_to_camel(table_name)
    schema = {
        "$ref": f"#/components/schemas/{table_name_camel}Return",
    }
    if list_response:
        schema = {
            "type": "array",
            "items": {  # type: ignore
                "$ref": f"#/components/schemas/{table_name_camel}Return",
            },
        }

    return {
        "200": {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "schema": schema,
                },
            },
        },
        **error_responses,
    }


def get_paths(table_name: str):
    """Get custom paths for openapi generation.

    Args:
        table_name: The table name to generate endpoint paths for.

    Returns:
        The newly created paths.
    """
    if settings.suppress_abstract_table_docs:
        if table_name in ["relationships", "operations"]:
            return {}

    table_name_camel = snake_to_camel(table_name)
    table_name_hyphenated = table_name.replace("_", "-")

    endpoints = {
        f"/v1/{table_name_hyphenated}": {
            "get": {
                "tags": [
                    table_name_camel,
                ],
                "summary": f"Get all {table_name_camel}",
                "operationId": f"get_{table_name}_v1__get",
                "parameters": [],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/FilterPayload"},
                        },
                    },
                },
                "responses": build_responses(table_name, True),
            },
            "post": {
                "tags": [
                    table_name_camel,
                ],
                "summary": f"Create a new {table_name_camel} resource",
                "operationId": f"create_{table_name}_v1__post",
                "parameters": [],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": f"#/components/schemas/{table_name_camel}Payload",
                            },
                        },
                    },
                    "required": "true",
                },
                "responses": build_responses(table_name),
            },
        },
        f"/v1/{table_name_hyphenated}/{{ "{{" }}resource_id{{ "}}" }}": {
            "get": {
                "tags": [
                    table_name_camel,
                ],
                "summary": f"Get a single {table_name_camel} resource",
                "operationId": f"get_{table_name}_v1__resource_id__get",
                "parameters": [
                    {
                        "description": f"The uuid of the {table_name_camel} resource.",
                        "required": "true",
                        "schema": {
                            "title": "Resource Id",
                            "type": "string",
                        },
                        "name": "resource_id",
                        "in": "path",
                    },
                ],
                "responses": build_responses(table_name),
            },
            "delete": {
                "tags": [
                    table_name_camel,
                ],
                "summary": f"Delete a {table_name_camel} resource",
                "operationId": f"delete_{table_name}_v1__resource_id__delete",
                "parameters": [
                    {
                        "description": f"The uuid of the {table_name_camel} resource.",
                        "required": "true",
                        "schema": {
                            "title": "Resource Id",
                            "type": "string",
                        },
                        "name": "resource_id",
                        "in": "path",
                    },
                ],
                "responses": build_responses(table_name),
            },
            "patch": {
                "tags": [
                    table_name_camel,
                ],
                "summary": f"Update a {table_name_camel} resource",
                "operationId": f"update_{table_name}_v1__resource_id__patch",
                "parameters": [
                    {
                        "description": f"The uuid of the {table_name_camel} resource.",
                        "required": "true",
                        "schema": {
                            "title": "Resource Id",
                            "type": "string",
                        },
                        "name": "resource_id",
                        "in": "path",
                    },
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": f"#/components/schemas/{table_name_camel}OptPayload",
                            },
                        },
                    },
                    "required": "true",
                },
                "responses": build_responses(table_name),
            },
        },
    }

    if table_name in ["relationships", "operations"]:
        return endpoints

    db = SessionLocal()

    operations = executioner.get_operations(table_name, db)

    if operations == {}:
        return {}

    if not operations.get("read_op"):
        del endpoints[f"/v1/{table_name_hyphenated}"]["get"]
        del endpoints[f"/v1/{table_name_hyphenated}/{{ "{{" }}resource_id{{ "}}" }}"]["get"]

    if not operations.get("create_op"):
        del endpoints[f"/v1/{table_name_hyphenated}"]["post"]

    if not operations.get("update_op"):
        del endpoints[f"/v1/{table_name_hyphenated}/{{ "{{" }}resource_id{{ "}}" }}"]["patch"]

    if not operations.get("delete_op"):
        del endpoints[f"/v1/{table_name_hyphenated}/{{ "{{" }}resource_id{{ "}}" }}"]["delete"]

    db.close()

    return endpoints


def get_schemas(table_name: str):
    """Get custom schemas for openapi doc generation.

    Args:
        table_name: The name of the table to generate schemas for.

    Returns:
        The newly created schemas.
    """
    new_schemas = {}

    schema_models = get_schema_models(table_name)

    for model in schema_models.values():
        schema = model.schema()
        new_schemas[schema["title"]] = schema

    new_schemas["Problem"] = problem_schema

    return new_schemas
