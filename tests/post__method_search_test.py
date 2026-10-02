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

def test_post_search_with_empty_query_returns_empty_list(client):
    response = client.post("/search", json={"query": ""})

    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == {"results": []}

def test_delete_document_removes_from_db_and_es(client, monkeypatch):
    deleted_from_db = []
    deleted_from_es = []

    def fake_delete_from_db(document_id):
        deleted_from_db.append(document_id)

    def fake_delete_from_index(document_id):
        deleted_from_es.append(document_id)

    monkeypatch.setattr(app_module, "delete_document_from_db", fake_delete_from_db)
    monkeypatch.setattr(app_module, "delete_document_from_index", fake_delete_from_index)

    response = client.delete("/documents/doc-1")

    assert response.status_code == 200
    assert deleted_from_db == ["doc-1"]
    assert deleted_from_es == ["doc-1"]
    assert response.get_json() == {"deleted": "doc-1"}