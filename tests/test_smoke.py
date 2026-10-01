from datetime import datetime, timezone

import pytest

from document_search_service.config import settings
from document_search_service.db import get_documents_by_ids, init_db, upsert_document
from document_search_service.es import get_es_client, index_document, init_index
from document_search_service.models import Document, IndexedDocument


def test_sqlite_document_roundtrip() -> None:
    init_db()

    document = Document(
        id="smoke-sqlite-1",
        rubrics=["news", "tech"],
        text="hello sqlite",
        created_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )

    upsert_document(document)

    loaded_documents = get_documents_by_ids([document.id])

    assert loaded_documents == [document]


def test_elasticsearch_smoke() -> None:
    es = get_es_client()

    try:
        es.info()
    except Exception:
        pytest.skip("Elasticsearch is not available")

    init_index(es)

    indexed_document = IndexedDocument(
        id="smoke-es-1",
        text="hello elasticsearch",
    )

    index_document(indexed_document, es=es, refresh=True)

    result = es.search(
        index=settings.es_index,
        query={
            "match": {
                "text": "elasticsearch",
            }
        },
    )

    assert result["hits"]["total"]["value"] >= 1