"""API routes for Organization resources."""
import re
from typing import Any, Dict, Optional
from uuid import UUID

from containerlog import get_logger
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session  # type: ignore

from ...db.exc import executioner
from ...db.session import metadata
from ...metadata import responses
from ...schema.v1.generic_models import FilterPayload
from ...utils.utils import get_schema_models, split_rtrim
from ..depends import get_db

logger = get_logger()
router = APIRouter()


@router.get(
    path="/{full_path:path}",
    summary="Get all resources",
    responses={
        **responses.common(401, 403, 500),
    },
)
async def get_resources(
    full_path: str,
    filter_payload: Optional[FilterPayload] = None,
    db: Session = Depends(get_db),
) -> Any:
    """Get all or a single resources.

    Args:
        full_path: The full path to validate and process.
        filter_payload: The optional filter payload to use.
        db: The database session to use for queries.

    Returns:
        Either the list of resources or a single resource.
    """
    # Validate full path
    if re.search(r"^[a-z-]+[\/]?[0-9a-z\-]*$", full_path) is None:
        raise HTTPException(status_code=500, detail="invalid path")

    split_path = split_rtrim(full_path, "/")

    resource_table_name = split_path[0].replace("-", "_")

    # Validate endpoint
    if resource_table_name not in metadata.tables.keys():
        raise HTTPException(status_code=404)

    operations = executioner.get_operations(resource_table_name, db)

    # Validate operation
    if not resource_table_name == "operations" and not operations.get("read_op"):
        raise NotImplementedError("route is not supported")

    schema_models = get_schema_models(resource_table_name)

    if len(split_path) > 1:
        resource_id = split_path[-1]

        # Validate UUID
        try:
            UUID(resource_id)
        except ValueError:
            raise HTTPException(status_code=500, detail="Malformed UUID")

        response = executioner.get_resource(resource_id, resource_table_name, db)

        # Validate response
        validated_response = schema_models["ModelReturn"](**response)

        return validated_response

    if filter_payload is not None:
        if filter_payload.ids is not None:
            for idx in filter_payload.ids:
                # Validate UUID
                try:
                    UUID(idx)
                except ValueError:
                    raise HTTPException(status_code=500, detail="Malformed UUID")

            response = executioner.get_some_resources(filter_payload.ids, resource_table_name, db)

            # Validate response
            validated_response = [schema_models["ModelReturn"](**data) for data in response]

            return validated_response

    response = executioner.get_resources(resource_table_name, db)

    # Validate response
    validated_response = [schema_models["ModelReturn"](**data) for data in response]

    return validated_response


@router.post(
    path="/{full_path:path}",
    summary="Create a new resource",
    responses={
        **responses.common(401, 403, 500),
    },
)
async def create_resource(
    payload: Dict[str, Any],
    full_path: str,
    db: Session = Depends(get_db),
) -> Any:
    """Create a new resource.

    Args:
        full_path: The full path.
        payload: The payload to create a new resource.
        db: The database session to use for queries.

    Returns:
        The newly created resource.
    """
    # Validate full path
    if len(full_path.split("/")) > 1:
        raise HTTPException(status_code=404)

    resource_table_name = full_path.split("/")[0].replace("-", "_")

    # Validate endpoint
    if resource_table_name not in metadata.tables.keys():
        raise HTTPException(status_code=404)

    operations = executioner.get_operations(resource_table_name, db)

    # Validate operation
    if not resource_table_name == "operations" and not operations.get("create_op"):
        raise NotImplementedError("route is not supported")

    # Validate payload
    schema_models = get_schema_models(resource_table_name)

    validated_payload = schema_models["ModelPayload"](**payload)

    response = executioner.create_resource(
        validated_payload,
        resource_table_name,
        db,
    )

    # Validate response
    validated_response = schema_models["ModelReturn"](**response)

    return validated_response


@router.patch(
    path="/{full_path:path}/{resource_id:str}",
    summary="Update a resource",
    responses={
        **responses.common(401, 403, 500),
    },
)
async def update_resource(
    payload: Dict[str, Any],
    full_path: str,
    resource_id: str,
    db: Session = Depends(get_db),
) -> Any:
    """Update a resource.

    Args:
        full_path: The full path.
        resource_id: The uuid of the resource.
        payload: The payload to update the resource with.
        db: The database session to use for queries.

    Returns:
        The updated resource.
    """
    # Validate full path
    if len(full_path.split("/")) > 1:
        raise HTTPException(status_code=404)

    resource_table_name = full_path.split("/")[0].replace("-", "_")

    # Validate endpoint
    if resource_table_name not in metadata.tables.keys():
        raise HTTPException(status_code=404)

    operations = executioner.get_operations(resource_table_name, db)

    # Validate operation
    if not resource_table_name == "operations" and not operations.get("update_op"):
        raise NotImplementedError("route is not supported")

    try:
        UUID(resource_id)
    except ValueError:
        raise HTTPException(status_code=500, detail="Malformed UUID")

    # Validate payload
    schema_models = get_schema_models(resource_table_name)

    validated_payload = schema_models["ModelOptPayload"](**payload)

    if validated_payload.dict() == {}:
        raise HTTPException(status_code=500, detail="Empty body")

    response = executioner.update_resource(
        resource_id,
        resource_table_name,
        validated_payload,
        db,
    )

    # Validate response
    validated_response = schema_models["ModelReturn"](**response)

    return validated_response


@router.delete(
    path="/{full_path:path}/{resource_id:str}",
    summary="Delete a resource",
    responses={
        **responses.common(401, 403, 500),
    },
)
async def delete_resource(
    full_path: str,
    resource_id: str,
    db: Session = Depends(get_db),
) -> Any:
    """Delete a resource.

    Args:
        full_path: The full path.
        resource_id: The uuid of the resource.
        db: The database session to use for queries.

    Returns:
        The deleted resource.
    """
    # Validate full path
    if len(full_path.split("/")) > 1:
        raise HTTPException(status_code=404)

    resource_table_name = full_path.split("/")[0].replace("-", "_")

    # Validate endpoint
    if resource_table_name not in metadata.tables.keys():
        raise HTTPException(status_code=404)

    operations = executioner.get_operations(resource_table_name, db)

    # Validate operation
    if not resource_table_name == "operations" and not operations.get("delete_op"):
        raise NotImplementedError("route is not supported")

    try:
        UUID(resource_id)
    except ValueError:
        raise HTTPException(status_code=500, detail="Malformed UUID")

    response = executioner.delete_resource(resource_id, resource_table_name, db)

    schema_models = get_schema_models(resource_table_name)

    # Validate response
    validated_response = schema_models["ModelReturn"](**response)

    return validated_response
