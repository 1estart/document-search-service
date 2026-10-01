from document_search_service import app as app_module


def test_post_search_returns_results(client, monkeypatch):
    fake_results = [
        {
            "id": "doc-1",
            "text": "hello",
        }
    ]

    captured = {}

    def fake_search_documents(query: str):
        captured["query"] = query
        return fake_results

    monkeypatch.setattr(
        app_module,
        "search_documents",
        fake_search_documents,
        raising=False,
    )

    response = client.post("/search", json={"query": "hello"})

    assert response.status_code == 200
    assert response.is_json
    assert captured["query"] == "hello"
    assert response.get_json() == {"results": fake_results}