from datetime import datetime, timezone

import pytest
import pytest_asyncio

from document_search_service import db, es
from document_search_service.models import Document, IndexedDocument


@pytest_asyncio.fixture(autouse=True)
async def _setup_infra():
    await db.init_db()
    await es.init_index()
    yield


@pytest.mark.asyncio
async def test_create_and_search(client):
    doc = Document(
        id="int-1",
        rubrics=["news"],
        text="интеграционный тест поиск",
        created_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
    )

    await db.upsert_document(doc)
    await es.index_document(IndexedDocument(id=doc.id, text=doc.text), refresh=True)

    response = await client.post("/search", json={"query": "интеграционный"})
    assert response.status_code == 200

    results = response.json()["results"]
    assert len(results) >= 1
    assert results[0]["id"] == "int-1"
    assert results[0]["text"] == "интеграционный тест поиск"
    assert results[0]["rubrics"] == ["news"]


@pytest.mark.asyncio
async def test_delete_removes_from_both_storages(client):
    doc = Document(
        id="int-del-1",
        rubrics=["test"],
        text="документ для удаления",
        created_date=datetime(2025, 6, 1, tzinfo=timezone.utc),
    )

    await db.upsert_document(doc)
    await es.index_document(IndexedDocument(id=doc.id, text=doc.text), refresh=True)

    found = await db.get_documents_by_ids(["int-del-1"])
    assert len(found) == 1

    response = await client.delete("/documents/int-del-1")
    assert response.status_code == 200

    found = await db.get_documents_by_ids(["int-del-1"])
    assert len(found) == 0

    response = await client.post("/search", json={"query": "удаления"})
    results = response.json()["results"]
    assert all(r["id"] != "int-del-1" for r in results)