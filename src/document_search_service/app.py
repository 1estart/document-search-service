import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

from . import db, es
from .config import settings
from .models import Document, IndexedDocument


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.init_db()
    await es.init_index()
    yield
    await db.close_pool()
    await es.close_es_client()


app = FastAPI(
    title="Document Search Service",
    description="Поиск документов через Elasticsearch + хранение в PostgreSQL",
    version="0.1.0",
    lifespan=lifespan,
)


class SearchRequest(BaseModel):
    query: str = ""


class SearchResponse(BaseModel):
    results: list[Document]


class CreateResponse(BaseModel):
    created: str


class DeleteResponse(BaseModel):
    deleted: str


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/stats")
async def stats() -> dict:
    es_client = await es.get_es_client()
    es_resp = await es_client.count(index=settings.es_index)
    es_count = es_resp["count"]

    p = await db.get_pool()
    async with p.acquire() as conn:
        pg_count = await conn.fetchval("SELECT COUNT(*) FROM documents")

    return {"es_count": es_count, "pg_count": pg_count}


async def search_documents(query: str) -> list[Document]:
    query = query.strip()

    if not query:
        return []

    client = await es.get_es_client()

    response = await client.search(
        index=settings.es_index,
        query={
            "multi_match": {
                "query": query,
                "fields": ["text", "text.english", "text.raw"],
            }
        },
        size=20,
    )

    ids = [hit["_id"] for hit in response["hits"]["hits"]]
    documents = await db.get_documents_by_ids(ids)

    return documents


@app.post("/search", response_model=SearchResponse)
async def search(payload: SearchRequest) -> SearchResponse:
    results = await search_documents(payload.query)
    return SearchResponse(results=results)


@app.post("/documents", response_model=CreateResponse, status_code=201)
async def create_document(document: Document) -> CreateResponse:
    await asyncio.gather(
        db.upsert_document(document),
        es.index_document(IndexedDocument(id=document.id, text=document.text)),
    )
    return CreateResponse(created=document.id)


@app.delete("/documents/{document_id}", response_model=DeleteResponse)
async def delete_document(document_id: str) -> DeleteResponse:
    await asyncio.gather(
        db.delete_document(document_id),
        es.delete_document(document_id),
    )
    return DeleteResponse(deleted=document_id)


@app.get("/docs.json")
async def openapi_spec():
    """Отдаём OpenAPI спецификацию для совместимости."""
    return app.openapi()