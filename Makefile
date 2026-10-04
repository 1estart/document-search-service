.PHONY: build up down logs load test

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down -v

logs:
	docker compose logs -f app

load:
	docker compose run --rm -v "$(CURDIR)/posts.csv:/app/posts.csv:ro" app uv run python -m document_search_service.load_posts

test:
	uv run pytest