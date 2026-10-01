import os

from elasticsearch import Elasticsearch

INDEX_NAME = os.getenv("ES_INDEX", "documents")
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")


def get_es_client() -> Elasticsearch:
    return Elasticsearch(ELASTICSEARCH_URL)


def init_index(es: Elasticsearch) -> None:
    if not es.indices.exists(index=INDEX_NAME):
        es.indices.create(
            index=INDEX_NAME,
            mappings={
                "properties": {
                    "id": {"type": "keyword"},
                    "text": {"type": "text"},
                }
            },
        )