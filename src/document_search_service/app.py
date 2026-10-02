from flask import Flask, jsonify, request
from .es import get_es_client
from .db import get_documents_by_ids
from .db import delete_document as delete_document_from_db
from .es import delete_document as delete_document_from_index
from .db import upsert_document
from .es import index_document
from .models import Document, IndexedDocument

from .config import settings

app = Flask(__name__)
app.json.ensure_ascii = False


@app.get("/health")
def health():
    return jsonify({"status": "ok"})

def search_documents(query: str) -> list[dict]:
    if not query.strip():
        return []
    
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

@app.delete("/documents/<document_id>")
def delete_document(document_id: str):
    delete_document_from_db(document_id)
    delete_document_from_index(document_id)

    return jsonify({"deleted": document_id})


@app.post("/documents")
def create_document():
    data = request.get_json()

    document = Document(**data)

    upsert_document(document)
    index_document(IndexedDocument(id=document.id, text=document.text))

    return jsonify({"created": document.id}), 201