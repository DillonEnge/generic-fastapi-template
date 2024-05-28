"""Database commands."""
from typing import Any, List

from fastapi.exceptions import HTTPException
from sqlalchemy import and_, delete, insert, or_, select, update  # type: ignore
from sqlalchemy.orm import Session  # type: ignore
from sqlalchemy.sql import func  # type: ignore

from ...builders.v1.generic_builders import build_resource
from ...utils.utils import dict_from_row, snake_to_camel, table_from_name

__all__ = [
    "get_operations",
    "get_resources",
    "get_resource",
    "create_resource",
    "update_resource",
    "delete_resource",
]


def get_resources(resource_table_name: str, db: Session) -> List[Any]:
    """Gets all resources.

    Args:
        resource_table_name: The table name of the resource.
        db: The database session to use for queries.

    Returns:
        The list of resources.
    """
    table_name_camel = snake_to_camel(resource_table_name)

    resource_table = table_from_name(resource_table_name)

    stmt = select(resource_table).where(resource_table.c.get("deleted_at") == None)

    results = db.execute(stmt).fetchall()

    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"{table_name_camel} not found",
        )

    built_resources = [build_resource(dict_from_row(result)) for result in results]

    for built_resource in built_resources:
        associations = get_associations(built_resource["id"], resource_table_name, db)

        for name, values in associations.items():
            built_resource[name] = values

    return built_resources


def get_some_resources(resource_ids: List[str], resource_table_name: str, db: Session) -> Any:
    """Gets some resources.

    Args:
        resource_ids: The uuids of the resources.
        resource_table_name: The table name of the resource.
        db: The database session to use for queries.

    Returns:
        The resources with the resource_ids.
    """
    table_name_camel = snake_to_camel(resource_table_name)

    resource_table = table_from_name(resource_table_name)

    stmt = select(resource_table).where(
        resource_table.c.id.in_(resource_ids),
        resource_table.c.get("deleted_at") == None,
    )

    results = db.execute(stmt).fetchall()

    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"{table_name_camel} resources not found",
        )

    built_resources = [build_resource(dict_from_row(result)) for result in results]

    for idx, built_resource in enumerate(built_resources):
        associations = get_associations(built_resource["id"], resource_table_name, db)

        for name, values in associations.items():
            built_resources[idx][name] = values

    return built_resources


def get_resource(resource_id: str, resource_table_name: str, db: Session) -> Any:
    """Gets a single resource.

    Args:
        resource_id: The uuid of the resource.
        resource_table_name: The table name of the resource.
        db: The database session to use for queries.

    Returns:
        The resource with the resource_id.
    """
    table_name_camel = snake_to_camel(resource_table_name)

    resource_table = table_from_name(resource_table_name)

    stmt = select(resource_table).where(
        resource_table.c.id == resource_id,
        resource_table.c.get("deleted_at") == None,
    )

    result = db.execute(stmt).first()

    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"{table_name_camel} resource not found",
        )

    built_resource = build_resource(dict_from_row(result))

    associations = get_associations(resource_id, resource_table_name, db)

    for name, values in associations.items():
        built_resource[name] = values

    return built_resource


def create_resource(
    payload: Any,
    resource_table_name: str,
    db: Session,
):
    """Create a new resource.

    Args:
        payload: The payload to create a new resource.
        resource_table_name: The table name of the resource.
        db: The database session to use for queries.

    Returns:
        The newly created resource.
    """
    table_name_camel = snake_to_camel(resource_table_name)

    resource_table = table_from_name(resource_table_name)

    mutable_payload = payload.dict()

    associative_fields = {}

    for key, value in mutable_payload.items():
        if isinstance(value, list):
            associative_fields[key] = value

    if associative_fields:
        for key in associative_fields.keys():
            del mutable_payload[key]

    stmt = insert(resource_table).values(mutable_payload).returning(resource_table)

    result = db.execute(stmt).first()

    if not result:
        raise HTTPException(status_code=500, detail=f"Unable to create {table_name_camel} resource")

    built_resource = build_resource(dict_from_row(result))

    if associative_fields:
        for key, associative_ids in associative_fields.items():
            built_resource[key] = associative_ids

            create_associations(built_resource["id"], resource_table_name, key, associative_ids, db)

    db.commit()

    return built_resource


def update_resource(
    resource_id: str,
    resource_table_name: str,
    payload: Any,
    db: Session,
) -> Any:
    """Update a resource.

    Args:
        resource_id: The uuid of the resource.
        payload: The payload to update the resource with.
        db: The database session to use for queries.

    Returns:
        The updated resource.
    """
    table_name_camel = snake_to_camel(resource_table_name)

    resource_table = table_from_name(resource_table_name)

    mutable_payload = payload.dict(exclude_unset=True)

    associative_fields = {}

    for key, value in mutable_payload.items():
        if isinstance(value, list):
            associative_fields[key] = value

    if associative_fields:
        for key in associative_fields.keys():
            del mutable_payload[key]

    stmt = None

    if mutable_payload:
        stmt = (
            update(resource_table)
            .where(resource_table.c.id == resource_id, resource_table.c.get("deleted_at") == None)
            .values(mutable_payload)
            .returning(resource_table)
        )
    else:
        stmt = select(resource_table).where(
            resource_table.c.id == resource_id, resource_table.c.get("deleted_at") == None
        )

    result = db.execute(stmt).first()

    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"{table_name_camel} resource not found",
        )

    built_resource = build_resource(dict_from_row(result))

    if associative_fields:
        for key, associative_ids in associative_fields.items():
            built_resource[key] = associative_ids

            update_associations(
                built_resource["id"],
                resource_table_name,
                key,
                [str(associative_id) for associative_id in associative_ids],
                db,
            )

    db.commit()

    return built_resource


def delete_resource(resource_id: str, resource_table_name: str, db: Session) -> Any:
    """Delete a resource.

    Args:
        resource_id: The uuid of the resource.
        resource_table_name: The table name of the resource.
        db: The database session to use for queries.

    Returns:
        The deleted resource.
    """
    table_name_camel = snake_to_camel(resource_table_name)

    resource_table = table_from_name(resource_table_name)

    stmt = None

    if "deleted_at" in resource_table.c.keys():
        stmt = (
            update(resource_table)
            .where(resource_table.c.id == resource_id, resource_table.c.deleted_at == None)
            .values(deleted_at=func.current_timestamp())
            .returning(resource_table)
        )
    else:
        stmt = (
            delete(resource_table)
            .where(resource_table.c.id == resource_id)
            .returning(resource_table)
        )

    result = db.execute(stmt).first()

    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"{table_name_camel} resource not found",
        )

    built_resource = build_resource(dict_from_row(result))

    associations = get_associations(resource_id, resource_table_name, db)

    if associations:
        for key, associative_ids in associations.items():
            built_resource[key] = associative_ids

            delete_associations(built_resource["id"], resource_table_name, key, associative_ids, db)

    db.commit()

    return built_resource


def get_associations(resource_id: str, table_name: str, db: Session) -> Any:
    """Get associations for a table.

    Args:
        resource_id: The uuid of the resource.
        table_name: The table name to get associations for.
        db: The database session to use for queries.

    Returns:
        The fetched table associations.
    """
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

    relationships = db.execute(stmt).fetchall()

    if not relationships:
        return {}

    relationships = [dict_from_row(relationship) for relationship in relationships]

    associations = {}

    for relationship in relationships:
        other_table_name = relationship["secondary_table_name"]

        if other_table_name == table_name:
            other_table_name = relationship["primary_table_name"]

        if relationship["associative_table_name"]:
            # Many to Many
            associative_table = table_from_name(relationship["associative_table_name"])

            stmt = select(associative_table.c[f"{other_table_name}_id"]).where(
                associative_table.c[f"{table_name}_id"] == resource_id
            )

            results = db.execute(stmt).fetchall()

            associations[other_table_name] = [
                dict_from_row(result)[f"{other_table_name}_id"] for result in results
            ]
        else:
            # One to Many
            secondary_table = table_from_name(other_table_name)

            foreign_key_ref = (
                relationship["primary_table_alias"]
                if relationship["primary_table_alias"]
                else f"{table_name}_id"
            )

            stmt = None

            if "deleted_at" in secondary_table.c.keys():
                stmt = select(secondary_table.c.id).where(
                    secondary_table.c[foreign_key_ref] == resource_id,
                    secondary_table.c["deleted_at"] == None,
                )
            else:
                stmt = select(secondary_table.c.id).where(
                    secondary_table.c[foreign_key_ref] == resource_id,
                )

            results = db.execute(stmt).fetchall()

            associations[other_table_name] = [dict_from_row(result)["id"] for result in results]

    return associations


def create_associations(
    primary_table_id: str,
    primary_table_name: str,
    secondary_table_name: str,
    associative_ids: List[str],
    db: Session,
):
    """Create associations for a table.

    Args:
        primary_table_id: The primary table id.
        primary_table_name: The primary table name.
        secondary_table_name: The secondary table name.
        associative_ids: The associative ids to associate with the primary table.
        db: The database session to use for queries.
    """
    relationships_table = table_from_name("relationships")

    stmt = select(relationships_table).where(
        or_(
            and_(
                relationships_table.c["primary_table_name"] == primary_table_name,
                relationships_table.c["secondary_table_name"] == secondary_table_name,
            ),
            and_(
                relationships_table.c["primary_table_name"] == secondary_table_name,
                relationships_table.c["secondary_table_name"] == primary_table_name,
            ),
        )
    )

    result = db.execute(stmt).first()

    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"relationship for {primary_table_name} resource not found",
        )

    relationship = build_resource(dict_from_row(result))

    associative_table = table_from_name(relationship["associative_table_name"])

    for associative_id in associative_ids:
        new_associative_row = {
            f"{primary_table_name}_id": str(primary_table_id),
            f"{secondary_table_name}_id": str(associative_id),
        }

        stmt = insert(associative_table).values(new_associative_row)

        db.execute(stmt)


def delete_associations(
    primary_table_id: str,
    primary_table_name: str,
    secondary_table_name: str,
    associative_ids: List[str],
    db: Session,
):
    """Delete associations for a table.

    Args:
        primary_table_id: The primary table id.
        primary_table_name: The primary table name.
        secondary_table_name: The secondary table name.
        associative_ids: The associative ids to dissociate with the primary table.
        db: The database session to use for queries.
    """
    relationships_table = table_from_name("relationships")

    stmt = select(relationships_table).where(
        or_(
            and_(
                relationships_table.c["primary_table_name"] == primary_table_name,
                relationships_table.c["secondary_table_name"] == secondary_table_name,
            ),
            and_(
                relationships_table.c["primary_table_name"] == secondary_table_name,
                relationships_table.c["secondary_table_name"] == primary_table_name,
            ),
        )
    )

    result = db.execute(stmt).first()

    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"relationship for {primary_table_name} resource not found",
        )

    relationship = build_resource(dict_from_row(result))

    associative_table = table_from_name(relationship["associative_table_name"])

    for associative_id in associative_ids:
        stmt = delete(associative_table).where(
            associative_table.c[f"{primary_table_name}_id"] == str(primary_table_id),
            associative_table.c[f"{secondary_table_name}_id"] == str(associative_id),
        )

        db.execute(stmt)


def update_associations(
    primary_table_id: str,
    primary_table_name: str,
    secondary_table_name: str,
    new_associative_ids: List[str],
    db: Session,
):
    """Update associations for a table.

    Args:
        primary_table_id: The primary table id.
        primary_table_name: The primary table name.
        secondary_table_name: The secondary table name.
        new_associative_ids: The new associative ids to associate with the primary table.
        db: The database session to use for queries.
    """
    associations = get_associations(primary_table_id, primary_table_name, db)

    current_associative_ids = associations[secondary_table_name]

    ids_to_delete = list(
        (set(current_associative_ids) & set(new_associative_ids)) ^ set(current_associative_ids)
    )
    ids_to_create = list(
        (set(current_associative_ids) & set(new_associative_ids)) ^ set(new_associative_ids)
    )

    if len(ids_to_delete) > 0:
        delete_associations(
            primary_table_id,
            primary_table_name,
            secondary_table_name,
            ids_to_delete,
            db,
        )

    if len(ids_to_create) > 0:
        create_associations(
            primary_table_id,
            primary_table_name,
            secondary_table_name,
            ids_to_create,
            db,
        )


def get_operations(table_name: str, db: Session) -> Any:
    """Get operations for a table.

    Args:
        table_name: The table name to get operations for.
        db: The database session to use for queries.

    Returns:
        The fetched table operations.
    """
    operations_table = table_from_name("operations")

    stmt = select(operations_table).where(operations_table.c.table_name == table_name)

    result = db.execute(stmt).first()

    if not result:
        return {}

    return build_resource(dict_from_row(result))
