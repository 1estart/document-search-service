#!/bin/sh
set -e

echo "Initializing database and Elasticsearch index..."
uv run python -m document_search_service.bootstrap
echo "Initialization complete. Starting server..."

exec "$@"