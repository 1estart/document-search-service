# document-search-service

Поиск документов через Elasticsearch + хранение в PostgreSQL. Асинхронный сервис на FastAPI.

## Требования

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Docker

## Установка

```bash
uv sync
```

---

## Функциональные тесты

### 1. Поднять стек

```bash
# Собрать образ и поднять контейнеры
make build
make up
```

Проверить, что всё готово:
```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

### 2. Загрузить данные

Загружаем `posts.csv` в базу и индексируем в Elasticsearch:

```bash
make load
```

### 3. Запустить функциональные тесты

```bash
uv run pytest tests/functional -v
```
---

## Остальные тесты

### Unit-тесты (быстрые, без Docker)

Проверяют логику изолированно, все зависимости мокаются.

```bash
uv run pytest tests/unit -v
```

### Интеграционные тесты (медленные, testcontainers)

Поднимают Elasticsearch и PostgreSQL в Docker-контейнерах на время тестов. Требуют запущенный Docker-демон, но не требуют `make up`.

```bash
uv run pytest tests/slow -v
```

### Запуск всех тестов

```bash
uv run pytest -v
```
---

Документация API (OpenAPI) автоматически доступна по адресам:
- `http://localhost:8000/docs` — Swagger UI
- `http://localhost:8000/redoc` — ReDoc
- `http://localhost:8000/openapi.json` — JSON-спецификация