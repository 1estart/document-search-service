# document-search-service

## Требования

- Python 3.12
- uv
- Docker для Elasticsearch и Postgres

## Установка зависимостей

```bash
uv sync
```

## Тесты
# Только быстрые unit-тесты (без Docker)
uv run pytest tests/unit -v

# Только медленные интеграционные (нужен Docker)
uv run pytest tests/slow -v

# Всё вместе
uv run pytest -v

## Поднятие всего в докер
# 1. Собрать образ
make build

# 2. Поднять сервисы (приложение + Elasticsearch)
make up

# 3. Загрузить данные из posts.csv (один раз)
make load

# 4. Проверить
curl http://localhost:8000/health
curl -X POST http://localhost:8000/search -H "Content-Type: application/json" -d '{"query": "привет"}'

# Логи приложения
make logs