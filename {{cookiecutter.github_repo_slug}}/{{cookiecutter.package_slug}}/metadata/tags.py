"""Definitions for the OpenAPI tags which are used by {{cookiecutter.package_title}}."""

# Tag strings describing the API resources involved.
health = "Health"


# This defines metadata for the tags listed above. The order in which the metadata
# entries are specified here will be the same order that the tag groups are displayed
# in the documentation.
# For additional details, see: https://fastapi.tiangolo.com/tutorial/metadata/#metadata-for-tags
tag_metadata = [
    {
        "name": health,
        "description": "Health status information for the application.",
    },
]
