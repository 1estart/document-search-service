import pytest


@pytest.mark.asyncio
async def test_search_russian_text(client):
    response = await client.post("/search", json={"query": "Мерседес"})
    assert response.status_code == 200
    results = response.json()["results"]
    if len(results) > 0:
        assert any("мерседес" in r["text"].lower() for r in results)


@pytest.mark.asyncio
async def test_search_case_insensitive(client):
    upper = await client.post("/search", json={"query": "МЕРСЕДЕС"})
    lower = await client.post("/search", json={"query": "мерседес"})

    upper_ids = {r["id"] for r in upper.json()["results"]}
    lower_ids = {r["id"] for r in lower.json()["results"]}

    assert upper_ids == lower_ids


@pytest.mark.asyncio
async def test_search_empty_query(client):
    response = await client.post("/search", json={"query": ""})
    assert response.status_code == 200
    assert response.json()["results"] == []