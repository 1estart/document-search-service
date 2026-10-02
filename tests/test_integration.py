import pytest
from datetime import datetime, timezone

from document_search_service.config import settings
from document_search_service.db import init_db, upsert_document
from document_search_service.es import get_es_client, index_document, init_index
from document_search_service.models import Document, IndexedDocument


@pytest.fixture
def integration_env(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "database_path", str(tmp_path / "test.db"))

    test_index = "test_documents"
    monkeypatch.setattr(settings, "es_index", test_index)

    es = get_es_client()
    try:
        es.info()
    except Exception:
        pytest.skip("Elasticsearch is not available")

    init_db()
    init_index(es)

    yield es

    if es.indices.exists(index=test_index):
        es.indices.delete(index=test_index)


def test_search_full_cycle(integration_env, client):
    es = integration_env

    doc = Document(
        id="int-test-1",
        rubrics=["test"],
        text="интеграционный тест поиск",
        created_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
    )

    upsert_document(doc)
    index_document(IndexedDocument(id=doc.id, text=doc.text), es=es, refresh=True)

    response = client.post("/search", json={"query": "интеграционный"})
    assert response.status_code == 200
    results = response.get_json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == "int-test-1"
    assert results[0]["text"] == "интеграционный тест поиск"
    assert results[0]["rubrics"] == ["test"]

    response = client.delete("/documents/int-test-1")
    assert response.status_code == 200

    response = client.post("/search", json={"query": "интеграционный"})
    results = response.get_json()["results"]
    assert len(results) == 0