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

## Загрузка тестового posts.csv
uv  run python src/document_search_service/load_posts.py

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

## Проверка search
```bash
curl -s -X POST http://127.0.0.1:5000/search   -H "Content-Type: application/json"   -d '{"query": "ВАЗ"}' | jq
curl -s -X POST http://127.0.0.1:5000/search   -H "Content-Type: application/json"   -d '{"query": "Мерседес"}' | jq
```


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