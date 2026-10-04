import pytest
from testcontainers.community.elasticsearch import ElasticSearchContainer
from testcontainers.community.postgres import PostgresContainer

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