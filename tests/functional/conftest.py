import pytest
import pytest_asyncio
from httpx2 import ASGITransport, AsyncClient

from document_search_service import db, es
from document_search_service.app import app


@pytest_asyncio.fixture()
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture(autouse=True)
async def _setup_and_teardown():
    db.pool = None
    es.client = None

    try:
        es_client = await es.get_es_client()
        await es_client.info()
    except Exception as e:
        pytest.skip(f"Elasticsearch недоступен: {e}")

    await db.init_db()
    await es.init_index()

    yield

    await db.close_pool()
    await es.close_es_client()