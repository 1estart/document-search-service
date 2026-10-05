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


## Next Steps

### Быстрые победы
- [ ] Добавить `ruff` (линт + формат) и `mypy` (типы) в `pyproject.toml`, цели `lint`/`format`/`typecheck` в `Makefile`
- [ ] Убрать неиспользуемые поля `host`, `port`, `workers` из `config.py`
- [ ] `/health` проверяет доступность БД и ЕС, возвращает `503` если что-то недоступно
- [ ] Единый формат ошибок через `exception_handler` в `app.py`

### Надёжность
- [ ] Компенсация при сбое: запись в БД → индекс → при ошибке откат БД (в `create_document`)
- [ ] Идемпотентное удаление: индекс → БД, оба не падают на отсутствующих документах
- [ ] Ретраи для запросов к ЕС (`max_retries`, `retry_on_status`)
- [ ] Graceful shutdown: закрытие пулов `asyncpg` и `AsyncElasticsearch` в `lifespan`

### Тесты
- [ ] Функциональные: дубликаты (upsert), валидация дат, спецсимволы, очень длинные запросы
- [ ] Конкурентность: параллельное создание, параллельный поиск
- [ ] `hypothesis` — property-based тесты для моделей и парсинга дат
- [ ] `schemathesis` — fuzzing по `openapi.json`
- [ ] `mutmut` — mutation testing для `src/`

### Инфраструктура
- [ ] CI в GitHub Actions: `lint` → `unit` → `slow` (с поднятием сервисов)
- [ ] Структурированное логирование (`structlog` или `logging` + JSON)
- [ ] Миграции БД через `alembic`
- [ ] Метрики (Prometheus) и трейсинг (OpenTelemetry)

### Фичи
- [ ] Пагинация в поиске (`page`/`size` или курсор)
- [ ] Ограничение размера `text` и `query` при создании/поиске
- [ ] Версионирование API: `/api/v1/search`, `/api/v1/documents`
- [ ] Кэширование результатов поиска (короткий TTL)