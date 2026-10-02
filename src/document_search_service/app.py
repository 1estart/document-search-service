from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory

from .config import settings
from .db import delete_document as delete_document_from_db
from .db import get_documents_by_ids, upsert_document
from .es import delete_document as delete_document_from_index
from .es import get_es_client, index_document
from .models import Document, IndexedDocument

app = Flask(__name__)
app.json.ensure_ascii = False

DOCS_DIR = Path(__file__).parent / "docs"

@app.get("/health")
def health():
    return jsonify({"status": "ok"})


def search_documents(query: str) -> list[dict]:
    if not query or not query.strip():
        return []

    es = get_es_client()
    response = es.search(
        index=settings.es_index,
        query={"match": {"text": query}},
        size=20,
    )

    ids = [hit["_id"] for hit in response["hits"]["hits"]]
    documents = get_documents_by_ids(ids)
    documents.sort(key=lambda doc: doc.created_date, reverse=True)

    return [doc.model_dump(mode="json") for doc in documents]


@app.post("/search")
def search():
    payload = request.get_json(silent=True) or {}
    query = payload.get("query", "")

    results = search_documents(query)
    return jsonify({"results": results})


@app.delete("/documents/<document_id>")
def delete_document(document_id: str):
    delete_document_from_db(document_id)
    delete_document_from_index(document_id)

    return jsonify({"deleted": document_id})


@app.post("/documents")
def create_document():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid or missing JSON payload"}), 400

    document = Document(**data)

    upsert_document(document)
    index_document(IndexedDocument(id=document.id, text=document.text))

    return jsonify({"created": document.id}), 201

@app.get("/docs.json")
def openapi_spec():
    return send_from_directory(DOCS_DIR, "docs.json", mimetype="application/json")

@app.get("/docs")
def swagger_ui():
    return """
    <!DOCTYPE html>
    <html>
      <head>
        <link rel="stylesheet"
              href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
      </head>
      <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
        <script>
          SwaggerUIBundle({
            url: "/docs.json",
            dom_id: "#swagger-ui",
          });
        </script>
      </body>
    </html>
    """