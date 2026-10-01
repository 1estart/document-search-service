from flask import Flask, jsonify, request
from .es import get_es_client
from .db import get_documents_by_ids
from .config import settings

app = Flask(__name__)


@app.get("/health")
def health():
    return jsonify({"status": "ok"})

def search_documents(query: str) -> list[dict]:
    es = get_es_client()

    response = es.search(
        index=settings.es_index,
        query={"match": {"text": query}},
        size=20,
    )

    ids = [hit["_id"] for hit in response["hits"]["hits"]]

    documents = get_documents_by_ids(ids)

    return [doc.model_dump(mode="json") for doc in documents]


@app.post("/search")
def search():
    payload = request.get_json(silent=True) or {}
    query = payload.get("query") or ""

    results = search_documents(query)

    return jsonify({"results": results})