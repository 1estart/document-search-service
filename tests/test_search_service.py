from datetime import datetime, timezone

from document_search_service import app as app_module
from document_search_service.models import Document


def test_search_documents_queries_es_and_db(monkeypatch):
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