from elasticsearch import AsyncElasticsearch

from .config import settings
from .models import IndexedDocument


client: AsyncElasticsearch | None = None


async def get_es_client() -> AsyncElasticsearch:
    global client
    if client is None:
        client = AsyncElasticsearch(
            settings.elasticsearch_url,
            connections_per_node=50,
            max_retries=3,
            retry_on_timeout=True,
        )
    return client


async def close_es_client() -> None:
    global client
    if client is not None:
        await client.close()
        client = None


async def init_index() -> None:
    es = await get_es_client()

    if not await es.indices.exists(index=settings.es_index):
        await es.indices.create(
            index=settings.es_index,
            settings={
                "analysis": {
                    "analyzer": {
                        "russian_analyzer": {"type": "russian"},
                        "english_analyzer": {"type": "english"},
                    }
                }
            },
            mappings={
                "properties": {
                    "id": {"type": "keyword"},
                    "text": {
                        "type": "text",
                        "analyzer": "russian_analyzer",
                        "fields": {
                            "english": {
                                "type": "text",
                                "analyzer": "english_analyzer",
                            },
                            "raw": {
                                "type": "text",
                                "analyzer": "standard",
                            }
                        }
                    },
                }
            },
        )


async def index_document(
    document: IndexedDocument,
    refresh: bool = True,
) -> None:
    es = await get_es_client()

    await es.index(
        index=settings.es_index,
        id=document.id,
        document=document.model_dump(),
        refresh=refresh,
    )


async def delete_document(document_id: str, refresh: bool = True) -> None:
    es = await get_es_client()

    await es.delete(
        index=settings.es_index,
        id=document_id,
        refresh=refresh,
    )