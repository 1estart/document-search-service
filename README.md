# document-search-service

## Требования

- Python 3.12
- uv
- Docker для Elasticsearch

## Установка зависимостей

```bash
uv sync
```

## Поднять Elasticsearch

```bash
docker run -d \
  --name elasticsearch \
  -p 9200:9200 \
  -e discovery.type=single-node \
  -e xpack.security.enabled=false \
  docker.elastic.co/elasticsearch/elasticsearch:8.15.0
```

## Тесты


```bash
uv run pytest
```

## Запуск Flask

```bash
uv run flask --app document_search_service.app run
```

## Проверка health

```bash
curl http://127.0.0.1:5000/health
```

Ожидаемый ответ:

```json
{"status":"ok"}
```