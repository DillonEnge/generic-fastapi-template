# {{cookiecutter.package_title}}

{{cookiecutter.package_description}}.

## Configuring

{{cookiecutter.package_title}} is configured through environment variables. This makes it easy to configure
the application whether run locally, as a container, or as part of a Helm deployment. Environment variables
may be provided by a `.env` file, similar to how the [local development deployment](#local-deployment) is
configured ([`dev/config.env`](dev/config.env)).

### Required

| Env Var | Description |
| ------- | ----------- |
| `APP_POSTGRES_HOST` | Hostname/address for the postgres instance to connect to. |
| `APP_POSTGRES_PORT` | Port for the postgres instance to connect to. |
| `APP_POSTGRES_USER` | Username for logging in to the postgres db. |
| `APP_POSTGRES_PASSWORD` | Password for logging in to the postgres db. |
| `APP_POSTGRES_DB` | The name of the database to use. |

### Optional

| Env Var | Description | Default |
| ------- | ----------- | ------- |
| `APP_SUPPRESS_ABSTRACT_TABLE_DOCS` | Suppress abstract table docs from generated documentation. | False |
| `APP_DEBUG` | Run the application with debug logging. | False |

## Developing

This project uses [poetry][poetry] for dependency and virtual environment management. Development commands are
declared as targets in the [Makefile](Makefile), and use `poetry` to run them within the project virtualenv.
To install the virtualenv and all production and development dependencies, simply

```
poetry install
```

As dependencies are added (`poetry add`), removed (`poetry remove`), or updated (`poetry update`), the virtualenv
is kept up-to-date.

### Local Deployment

To simplify the developer flow, a local development deployment has been set up which includes:

- `{{cookiecutter.package_slug}}`, running on-host (port {{cookiecutter.default_port}})
- `postgresql`, running in a container (port 5432)
- `pgadmin`, running in a container (port 16543)

The configurations for all running services can be found in the [`dev/`](dev) directory.
Of note, [dev/config/pg-init.d](dev/config/pg-init.d) contains SQL files which are applied in order when
postgres starts up. This is where tables and data are defined for the development postgres instance. 
**Care should be taken to ensure the table schema stay up-to-date with the production database schema.**

The local deployment can be started with `make dev` and stopped with `make down`.

#### API Docs

Once running, API docs can be found at `/docs` or `/redoc`.

#### Using pgAdmin

To use pgAdmin, go to `localhost:16543` with the local deployment running. Login in with email `{{cookiecutter.author_email}}` and
password `admin`. From there, you will need to "Add New Server".

In the "Create Server" modal, give it a name (e.g. "local-dev"), then go to the "Connection" tab, and set:

- Hostname/address: `postgres`
- Port: `5432`
- Maintenance database: `root`
- Username: `root`
- Password: `root`

Save, and pgAdmin should now be connected to the local development database instance.

### PGAdmin ERD
The entity relationship diagram functionality is only available when a single database instance is selected in pgAdmin.
After following the steps above to add a server, expand in the tree until the postgres databases instance is visible.
Select that DB and then select Tools > ERD Tool from the top menu. This repo is configured to mount the local directory [/data-api/dev/schemas/](dev/schemas)
into the pgAdmin container. This allows for the loading of `.pgerd` ERD files from this repo into pgAdmin for viewing, as well as supporting creation of new ERDs
or modifications of existing ERDs that will be recognized as changes to the repo by Github. A short overview of pgAdmin's ERD functionality is available on [youTube][youTube]

#### Gotchas

- When updating table schema or adding/removing postgres data via the config in [dev/config/pg-init.d](dev/config/pg-init.d),
  it is important to remove any old containers so postgres can start fresh. Otherwise, it won't pick up the changes.

[poetry]: https://python-poetry.org/
[youTube]: https://youtu.be/2pxVCzRFGeg
