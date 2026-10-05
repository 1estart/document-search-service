import pytest


@pytest.mark.asyncio
async def test_user_creates_document_and_finds_it(client):
    doc = {
        "id": "user-doc-func-1",
        "rubrics": ["test"],
        "text": "уникальный текст для функционального теста zxcvbn",
        "created_date": "2026-01-01T00:00:00Z",
    }
    create_resp = await client.post("/documents", json=doc)
    assert create_resp.status_code == 201

    search_resp = await client.post(
        "/search", json={"query": "zxcvbn"}
    )
    assert search_resp.status_code == 200
    results = search_resp.json()["results"]
    assert any(r["id"] == "user-doc-func-1" for r in results)


@pytest.mark.asyncio
async def test_user_deletes_document_and_cannot_find_it(client):
    doc = {
        "id": "user-doc-func-2",
        "rubrics": ["test"],
        "text": "документ который удалим qwerty12345",
        "created_date": "2026-01-01T00:00:00Z",
    }
    await client.post("/documents", json=doc)

    search_resp = await client.post("/search", json={"query": "qwerty12345"})
    assert any(r["id"] == "user-doc-func-2" for r in search_resp.json()["results"])

    delete_resp = await client.delete("/documents/user-doc-func-2")
    assert delete_resp.status_code == 200

    search_resp = await client.post("/search", json={"query": "qwerty12345"})
    assert not any(r["id"] == "user-doc-func-2" for r in search_resp.json()["results"])