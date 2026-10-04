import pytest
import pytest_asyncio
from httpx2 import ASGITransport, AsyncClient
from testcontainers.community.elasticsearch import ElasticSearchContainer
from testcontainers.community.postgres import PostgresContainer

from document_search_service import db, es
from document_search_service.app import app
from document_search_service.config import settings


@pytest.fixture(scope="session")
def es_container():
    with ElasticSearchContainer("elasticsearch:8.15.3") as container:
        yield container


@pytest.fixture(scope="session")
def pg_container():
    with PostgresContainer("postgres:16-alpine") as container:
        yield container


def _es_url(container: ElasticSearchContainer) -> str:
    host = container.get_container_host_ip()
    port = container.get_exposed_port(9200)
    return f"http://{host}:{port}"


def _pg_url(container: PostgresContainer) -> str:
    url = container.get_connection_url()
    return url.replace("postgresql+psycopg2://", "postgresql://", 1)


@pytest.fixture(autouse=True)
def _override_settings(es_container, pg_container, monkeypatch):
    monkeypatch.setattr(settings, "elasticsearch_url", _es_url(es_container))
    monkeypatch.setattr(settings, "database_url", _pg_url(pg_container))
    monkeypatch.setattr(settings, "es_index", "test_documents")


@pytest_asyncio.fixture(autouse=True)
async def _reset_connections():
    db.pool = None
    es.client = None
    
    yield
    
    await db.close_pool()
    await es.close_es_client()


@pytest_asyncio.fixture()
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac