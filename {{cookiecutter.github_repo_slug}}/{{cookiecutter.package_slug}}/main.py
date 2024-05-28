"""Main entry point for {{cookiecutter.package_title}}.

This file contains an app builder and a global reference to `app`, the instance
of a FastAPI server for {{cookiecutter.package_title}}. This `app` instance should be used as
the target for uvicorn.
"""
import containerlog.proxy.std
import fastapi_rfc7807.middleware as rfc7807
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from . import middleware
from .api import core, generic
from .core import events, hooks
from .core.config import settings
from .metadata import tags
from .utils.utils import (
    generate_custom_openapi_paths,
    generate_custom_openapi_schemas,
    generate_custom_openapi_tags,
)

# Patch the uvicorn, fastapi, and websockets std loggers to use the containerlog
# proxy. This gives us not only faster logging, but also consistently formatted
# log messages across the different 3rd party libraries.
containerlog.proxy.std.patch("uvicorn*", "fastapi", "websockets*")


# Set up application logging. If DEBUG is not configured, run the application
# at INFO level. Since containerlog defaults to debug logging, just check if
# it should be set to INFO.
if not settings.debug:
    containerlog.set_level(containerlog.INFO)  # pragma: nocover


def get_application() -> FastAPI:
    """Get an instance of a FastAPI application fully configured for {{cookiecutter.package_title}}."""

    application = FastAPI(
        title="{{cookiecutter.package_title}}",
        description="{{cookiecutter.package_description}}.",
        version="v1",
        # Note: typically this would expose stack traces to the caller when exceptions
        # are raised. Because we are using the fastapi_rfc7807 middleware, the error
        # handler it provides overrides the default handler which exposes this info,
        # so setting to debug mode here should not leak stack traces externally.
        debug=settings.debug,
        openapi_tags=tags.tag_metadata,
    )

    # Define "pre" and "post" hooks off the application state which are later
    # registered to the rfc7807 error handling middleware. These hooks allow
    # actions to take place before and after the creation (but before the return)
    # of an error response. Hooks may be added by other application middleware
    # upon registration.
    application.state.pre_hooks = [
        hooks.log_exc,  # Log full exception traceback on error
    ]
    application.state.post_hooks = []

    # Register the API routes
    application.include_router(core.router)

    # Must be the last router registered to act as a fall-through
    application.include_router(generic.router)

    # Register application middleware
    middleware.prometheus.register(application)

    # Traps exceptions and raises error responses in RFC7807 format.
    rfc7807.register(
        app=application,
        pre_hooks=application.state.pre_hooks,
        post_hooks=application.state.post_hooks,
        add_schema=True,
    )

    # Register application event handlers
    events.register_startup(application)
    events.register_shutdown(application)

    def custom_openapi():
        if application.openapi_schema:
            return application.openapi_schema

        openapi_schema = get_openapi(
            title=application.title,
            version=application.version,
            description=application.description,
            routes=application.routes,
        )

        del openapi_schema["paths"]["/v1/{full_path}"]
        del openapi_schema["paths"]["/v1/{full_path}/{resource_id}"]

        new_paths = generate_custom_openapi_paths()

        for path, definition in new_paths.items():
            if path in openapi_schema["paths"].keys():
                for method, schema in definition.items():
                    if method not in openapi_schema["paths"][path].keys():
                        openapi_schema["paths"][path][method] = schema
            else:
                openapi_schema["paths"][path] = definition

        new_schemas = generate_custom_openapi_schemas()

        for schema_name, definition in new_schemas.items():
            openapi_schema["components"]["schemas"][schema_name] = definition

        new_tags = generate_custom_openapi_tags()

        openapi_schema["tags"] = new_tags

        application.openapi_schema = openapi_schema

        return application.openapi_schema

    application.openapi = custom_openapi  # type: ignore

    return application


# Global reference to `app` so uvicorn and load and run it.
app: FastAPI = get_application()
