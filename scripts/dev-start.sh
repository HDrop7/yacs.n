#!/usr/bin/env bash
if command -v docker-compose &> /dev/null; then
  docker-compose \
    -f docker-compose.yml \
    -f docker-compose.development.yml \
    up
else
docker compose \
  -f docker-compose.yml \
  -f docker-compose.development.yml \
  up
fi
