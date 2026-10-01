from flask import Flask, jsonify, request

app = Flask(__name__)


@app.get("/health")
def health():
    return jsonify({"status": "ok"})

def search_documents(query: str) -> list[dict]:
    return []


@app.post("/search")
def search():
    payload = request.get_json(silent=True) or {}
    query = payload.get("query") or ""

    results = search_documents(query)

    return jsonify({"results": results})