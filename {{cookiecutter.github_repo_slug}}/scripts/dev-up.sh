#!/usr/bin/env bash
#
# dev-up.sh
#
# Start the local development deployment consisting of {{cookiecutter.package_slug}}
# and dependent backend services to mock out a "real" service deployment.
#

RED='\033[0;31m'
NC='\033[0m' # No Color
ERROR="${RED}error${NC}: "

echo "Starting local development deployment dependencies..."

docker-compose \
  -f dev/dependencies.yaml \
  up -d

echo "Local deployment dependencies started."
echo "-------------------------------------"
docker ps --format '{{ "{{" }}.Names{{ "}}" }}:\t{{ "{{" }}.Ports{{ "}}" }}'
echo "-------------------------------------"
echo "To terminate the dependencies, run 'make down'."

echo ""
echo "Starting {{cookiecutter.github_repo_slug}}..."
echo "Following {{cookiecutter.github_repo_slug}} logs (ctrl C to stop)..."

docker logs {{cookiecutter.package_slug}} -f
