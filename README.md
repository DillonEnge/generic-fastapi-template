# Generic FastAPI Application Cookiecutter

A [cookiecutter][cookiecutter] template for FastAPI-based applications.

This template serves as a starting point for creating a new FastAPI-based microservice application. While it
aims to provide a lot of the core repository setup, tooling integration, and organization "best practices",
you should feel free to modify your project to use whatever structure, features, tooling, and workflows you
need for your specific use case. This will just help you get off the ground running.

## Features

- Basic FastAPI application with support for:
    - Structured logging with [containerlog][containerlog]
    - RFC7807-formatted errors with [fastapi-rfc7807][fastapi-rfc7807]
    - Prometheus metrics middleware
    - Environment-based configuration with [pydantic][pydantic-settings]
    - Versioned API routes
    - Versioned Models and Schema
- Development workflow targets with [GNU Make][make]
- Dependency and virtualenv management with [poetry][poetry]
- Unit tests with [pytest][pytest]
- Source code formatting with [black][black]
- Source code linting with [flake8][flake8]
- Import sorting with [isort][isort]
- Static type checking with [mypy][mypy]
- Git hooks for formatting actions with [pre-commit][pre-commit]
- Dockerfile for containerization with [Docker][docker]
- Local development deployment orchestrated with [docker compose][docker-compose]

## Template Configuration

| Option | Description |
| ------ | ----------- |
| `default_port`       | The default port for the project. |
| `author_email`       | The email of the user. |
| `github_repo_slug`   | The name of the project's repository. |
| `github_repo_owner`  | The github username of the user. |
| `docker_username`    | The docker username of the user. |
| `package_description`| A short description of what the project is. This is used in the README and in project metadata. |
| `package_slug`       | The internal python package slug for this project. |
| `package_title`      | The title of this project. This is used in the Makefile, Dockerfile, and main entrypoint. |

## Guide

Below is a basic step-by-step guide on generating a new project using this template.

To get started, you will need [cookiecutter][cookiecutter], [poetry][poetry], and [pyenv][pyenv] installed.

### Generate a new project from template

You can either clone this repo down and point to your local copy
when generating a project, or point to the repository itself.

```console
$ cookiecutter git+ssh://git@github.com/DillonEnge/generic-fastapi-template.git -o path/to/output
```

```console
$ cookiecutter git+ssh://git@github.com/DillonEnge/generic-fastapi-template.git -o path/to/output
package_title [Generic Fastapi Template]: New Service
default_port [8989]:
author_email [author@email.com]:
github_repo_slug [new-service]:
github_repo_owner [MyGithubUsername]:
docker_username: [MyDockerUsername]:
package_description [Generic fastapi template]: A brand new example microservice
package_slug [new_service]:
```

```console
$ cd /path/to/output/new-service
```

New projects are configured for Python 3.9, so we will want to set the local Python version
accordingly. If you haven't installed 3.9 with pyenv yet, do so now.

```console
$ pyenv local 3.9.0
```

Now we can set up our virtualenv and install project dependencies into it with poetry.

```console
$ poetry install
```
