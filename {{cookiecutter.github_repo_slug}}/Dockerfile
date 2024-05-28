# ---
# build - compile dependencies and package the project
#
FROM python:3.9.19-bookworm AS build

RUN pip install --disable-pip-version-check poetry

WORKDIR /build
COPY . .

RUN poetry export -f requirements.txt -o requirements.txt \
 && poetry build -f sdist

RUN pip install \
      --no-cache-dir \
      --disable-pip-version-check \
      --no-warn-script-location \
      -r requirements.txt


# ---
# base - set up shared environment and install dependencies
#
FROM python:3.9.19-slim-bookworm as base

# PYTHONUNBUFFERED: allow stdin, stdout, and stderr to be totally unbuffered.
#   This is required so that the container logs are rendered as they are logged into
#   `docker logs`.
ENV PYTHONUNBUFFERED=1

# Copy artifacts from the build stage
COPY --from=build /build/dist/{{cookiecutter.package_slug}}-*.tar.gz /app/{{cookiecutter.package_slug}}.tar.gz
COPY --from=build /usr/local/lib/python3.9 /usr/local/lib/python3.9
COPY --from=build /usr/local/bin/uvicorn /usr/local/bin/uvicorn

# Install additional project dependencies
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
   libpq-dev \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app


# ---
# dev - image for local development
#
FROM base as dev

# Note: this expects the project directory to be volume-mounted into /app
CMD ["uvicorn", "{{cookiecutter.package_slug}}.main:app", "--host", "0.0.0.0", "--port", "{{cookiecutter.default_port}}", "--reload"]


# ---
# prod - production image used for deployments
#
FROM base as prod

RUN pip install {{cookiecutter.package_slug}}.tar.gz

ARG VCS_REF=unknown
ARG BUILD_VERSION=canary
ARG BUILD_DATE=unknown

LABEL org.opencontainers.image.title="{{cookiecutter.package_title}}" \
      org.opencontainers.image.source="https://github.com/{{cookiecutter.github_repo_owner}}/{{cookiecutter.github_repo_slug}}.git" \
      org.opencontainers.image.url="https://github.com/{{cookiecutter.github_repo_owner}}/{{cookiecutter.github_repo_slug}}" \
      org.opencontainers.image.authors="{{cookiecutter.author_email}}" \
      org.opencontainers.image.revision=$VCS_REF \
      org.opencontainers.image.version=$BUILD_VERSION \
      org.opencontainers.image.created=$BUILD_DATE

ENTRYPOINT ["uvicorn", "{{cookiecutter.package_slug}}.main:app", "--host", "0.0.0.0", "--port", "{{cookiecutter.default_port}}"]
