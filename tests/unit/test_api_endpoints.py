from datetime import datetime, timezone

from document_search_service import app as app_module
from document_search_service.models import Document


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_search_returns_results(client, monkeypatch):
    fake_results = [
        Document(
            id="doc-1",
            rubrics=["news"],
            text="hello world",
            created_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
    ]

    async def fake_search_documents(query: str):
        return fake_results

    monkeypatch.setattr(app_module, "search_documents", fake_search_documents)

    response = client.post("/search", json={"query": "hello"})

    assert response.status_code == 200
    assert response.json() == {
        "results": [
            {
                "id": "doc-1",
                "rubrics": ["news"],
                "text": "hello world",
                "created_date": "2026-01-01T00:00:00Z",
            }
        ]
    }


def test_search_empty_query_returns_empty(client):
    response = client.post("/search", json={"query": ""})
    assert response.status_code == 200
    assert response.json() == {"results": []}


def test_create_document_saves_to_db_and_es(client, monkeypatch):
    created_in_db = []
    created_in_es = []

    async def fake_upsert_document(document):
        created_in_db.append(document)

    async def fake_index_document(document, **kwargs):
        created_in_es.append(document)

    monkeypatch.setattr(app_module.db, "upsert_document", fake_upsert_document)
    monkeypatch.setattr(app_module.es, "index_document", fake_index_document)

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
    assert response.json() == {"created": "doc-new"}


def test_delete_document_removes_from_db_and_es(client, monkeypatch):
    deleted_from_db = []
    deleted_from_es = []

    async def fake_delete_from_db(document_id):
        deleted_from_db.append(document_id)

    async def fake_delete_from_index(document_id, **kwargs):
        deleted_from_es.append(document_id)

    monkeypatch.setattr(app_module.db, "delete_document", fake_delete_from_db)
    monkeypatch.setattr(app_module.es, "delete_document", fake_delete_from_index)

    response = client.delete("/documents/doc-42")

    assert response.status_code == 200
    assert deleted_from_db == ["doc-42"]
    assert deleted_from_es == ["doc-42"]
    assert response.json() == {"deleted": "doc-42"}