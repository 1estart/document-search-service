from elasticsearch import Elasticsearch

from .config import settings
from .models import IndexedDocument


def get_es_client() -> Elasticsearch:
    return Elasticsearch(settings.elasticsearch_url)


def init_index(es: Elasticsearch | None = None) -> Elasticsearch:
    client = es or get_es_client()

    if not client.indices.exists(index=settings.es_index):
        client.indices.create(
            index=settings.es_index,
            mappings={
                "properties": {
                    "id": {"type": "keyword"},
                    "text": {"type": "text"},
                }
            },
        )

    return client


def index_document(
    document: IndexedDocument,
    es: Elasticsearch | None = None,
    refresh: bool = True,
) -> None:
    client = es or get_es_client()

    client.index(
        index=settings.es_index,
        id=document.id,
        document=document.model_dump(),
        refresh=refresh,
    )


def delete_document(
    document_id: str,
    es: Elasticsearch | None = None,
    refresh: bool = True,
) -> None:
    client = es or get_es_client()

    client.delete(
        index=settings.es_index,
        id=document_id,
        refresh=refresh,
    )