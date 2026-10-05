import pytest


@pytest.mark.asyncio
async def test_search_nonexistent_returns_empty(client):
    response = await client.post(
        "/search", json={"query": "абракадабра_которой_нет_в_базе_xyz123"}
    )
    assert response.status_code == 200
    assert response.json()["results"] == []


@pytest.mark.asyncio
async def test_create_document_without_required_fields(client):
    response = await client.post("/documents", json={"id": "doc-1"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_nonexistent_document(client):
    response = await client.delete("/documents/nonexistent-doc-xyz123")
    assert response.status_code == 200