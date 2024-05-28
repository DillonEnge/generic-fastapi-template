#!/usr/bin/env bash
#
# dev-down.sh
#
# Terminate the local development deployment (started via dev-up.sh) if
# it is running, and clean up any remaining artifacts.
#

echo "Terminating local development deployment..."

docker-compose \
  -f dev/dependencies.yaml \
  down

echo "[done]"
