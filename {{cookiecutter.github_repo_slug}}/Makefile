#
# {{cookiecutter.package_title}}
#

PKG_NAME    := {{cookiecutter.package_slug}}
PKG_VERSION := $(shell poetry version | awk '{print $$2}')
IMAGE_NAME  := {{cookiecutter.docker_username}}/{{cookiecutter.github_repo_slug}}

.PHONY: apidoc clean cover dev down docker fmt github-tag lint requirements test update version help
.DEFAULT_GOAL := help


apidoc: docker  ## Open the latest version of the project's OpenAPI docs
	open http://localhost:9011/docs
	@docker run -p 9011:8000 --rm --name ${PKG_NAME}-apidoc ${IMAGE_NAME}

clean:  ## Clean up build and test artifacts
	rm -rf build/ dist/ *.egg-info src/*.egg-info htmlcov/ .coverage* .pytest_cache/ \
		${PKG_NAME}/__pycache__ tests/__pycache__

cover: test  ## Run unit tests and open the resulting HTML coverage report
	open ./htmlcov/index.html

dev:  ## Run a local development deployment with backend services
	@./scripts/dev-up.sh

down:  ## Terminate the local development deployment, if running
	@./scripts/dev-down.sh

docker:  ## Build the docker image
	@# Build and tag the build stage since it is more intensive. This allows
	@# us to use the cache without having to continually rebuild it.
	docker build --target=build \
		--cache-from=${IMAGE_NAME}:build \
		-t ${IMAGE_NAME}:build .
	docker build --target=base \
		--cache-from=${IMAGE_NAME}:build \
		--cache-from=${IMAGE_NAME}:base \
		-t ${IMAGE_NAME}:base .
	docker build \
		--cache-from=${IMAGE_NAME}:build \
		--cache-from=${IMAGE_NAME}:base \
		-t ${IMAGE_NAME}:latest .

fmt:  ## Automatic source code formatting
	poetry run pre-commit run --all-files

github-tag:  ## Create and push a tag with the current version
	git tag -a ${PKG_VERSION} -m "${PKG_NAME} version ${PKG_VERSION}"
	git push -u origin ${PKG_VERSION}

lint:  ## Run linting checks on the project source code
	poetry run flake8
	poetry run mypy ${PKG_NAME}
	poetry check

requirements:  ## Generate the requirements.txt file
	poetry export -f requirements.txt > requirements.txt

test:  ## Run the unit tests
	poetry run env $$(cat tests/unit.env | xargs) pytest -s -vv --cov ${PKG_NAME} --cov-report html --cov-report term-missing --cov-fail-under=100 --cov-branch

update:  ## Update project and tooling dependencies.
	poetry update
	poetry run pre-commit autoupdate

version:  ## Print the application version
	@echo "${PKG_VERSION}"

help:  ## Print Make usage information
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_-]+:.*?## / {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort


.PHONY: unit-test setup

unit-test: test

setup:
	poetry install
