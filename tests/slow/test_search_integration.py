from datetime import datetime, timezone

import pytest

from document_search_service.app import search_documents
from document_search_service.db import get_documents_by_ids, init_db, upsert_document
from document_search_service.es import get_es_client, index_document, init_index
from document_search_service.models import Document, IndexedDocument


@pytest.fixture(autouse=True)
def _setup_infra():
    init_db()
    es = get_es_client()
    init_index(es)
    return es


class TestSearchFullCycle:
    def test_create_and_search(self, client):
        doc = Document(
            id="int-1",
            rubrics=["news"],
            text="интеграционный тест поиск",
            created_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
        )
        upsert_document(doc)
        index_document(IndexedDocument(id=doc.id, text=doc.text), refresh=True)

        response = client.post("/search", json={"query": "интеграционный"})
        assert response.status_code == 200

        results = response.get_json()["results"]
        assert len(results) >= 1
        assert results[0]["id"] == "int-1"
        assert results[0]["text"] == "интеграционный тест поиск"
        assert results[0]["rubrics"] == ["news"]

    def test_delete_removes_from_both_storages(self, client):
        doc = Document(
            id="int-del-1",
            rubrics=["test"],
            text="документ для удаления",
            created_date=datetime(2025, 6, 1, tzinfo=timezone.utc),
        )
        upsert_document(doc)
        index_document(IndexedDocument(id=doc.id, text=doc.text), refresh=True)

        found = get_documents_by_ids(["int-del-1"])
        assert len(found) == 1

        response = client.delete("/documents/int-del-1")
        assert response.status_code == 200

        found = get_documents_by_ids(["int-del-1"])
        assert len(found) == 0

        results = search_documents("удаления")
        assert all(r["id"] != "int-del-1" for r in results)