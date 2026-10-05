import pytest


@pytest.mark.asyncio
async def test_search_returns_max_20_results(client):
    response = await client.post("/search", json={"query": "и"})
    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) <= 20


@pytest.mark.asyncio
async def test_search_results_sorted_by_date_desc(client):
    response = await client.post("/search", json={"query": "и"})
    assert response.status_code == 200
    results = response.json()["results"]

    dates = [r["created_date"] for r in results]
    assert dates == sorted(dates, reverse=True)