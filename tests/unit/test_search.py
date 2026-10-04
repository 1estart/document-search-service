# tests/unit/test_search.py
from datetime import datetime, timezone

from document_search_service import app as app_module
from document_search_service.models import Document


class TestSearchDocumentsUnit:
    def test_queries_es_and_db(self, monkeypatch):
        fake_es_response = {
            "hits": {
                "hits": [
                    {"_id": "doc-1"},
                    {"_id": "doc-2"},
                ]
            }
        }

        class FakeES:
            def search(self, index, query, size):
                assert index == "documents"
                assert query == {"match": {"text": "hello"}}
                assert size == 20
                return fake_es_response

        monkeypatch.setattr(app_module, "get_es_client", lambda: FakeES())

        doc1 = Document(
            id="doc-1",
            rubrics=["news"],
            text="hello world",
            created_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        doc2 = Document(
            id="doc-2",
            rubrics=["tech"],
            text="hello flask",
            created_date=datetime(2026, 1, 2, tzinfo=timezone.utc),
        )

        def fake_get_documents_by_ids(ids):
            assert ids == ["doc-1", "doc-2"]
            return [doc1, doc2]

        monkeypatch.setattr(app_module, "get_documents_by_ids", fake_get_documents_by_ids)

        result = app_module.search_documents("hello")

        assert result == [
            doc2.model_dump(mode="json"),
            doc1.model_dump(mode="json"),
        ]

    def test_empty_query_returns_empty(self, client):
        response = client.post("/search", json={"query": ""})
        assert response.status_code == 200
        assert response.get_json() == {"results": []}


class TestDeleteDocumentUnit:
    def test_calls_db_and_es(self, client, monkeypatch):
        deleted_from_db = []
        deleted_from_es = []

        monkeypatch.setattr(
            app_module, "delete_document_from_db", lambda doc_id: deleted_from_db.append(doc_id)
        )
        monkeypatch.setattr(
            app_module, "delete_document_from_index", lambda doc_id: deleted_from_es.append(doc_id)
        )

        response = client.delete("/documents/doc-42")

        assert response.status_code == 200
        assert deleted_from_db == ["doc-42"]
        assert deleted_from_es == ["doc-42"]
        assert response.get_json() == {"deleted": "doc-42"}


class TestCreateDocumentUnit:
    def test_creates_in_db_and_es(self, client, monkeypatch):
        created_in_db = []
        created_in_es = []

        monkeypatch.setattr(app_module, "upsert_document", lambda doc: created_in_db.append(doc))
        monkeypatch.setattr(app_module, "index_document", lambda doc, **kw: created_in_es.append(doc))

        response = client.post(
            "/documents",
            json={
                "id": "doc-new",
                "rubrics": ["news"],
                "text": "hello",
                "created_date": "2026-01-01T00:00:00Z",
            },
        )

        assert response.status_code == 201
        assert created_in_db[0].id == "doc-new"
        assert created_in_es[0].id == "doc-new"