import pytest
from fastapi.testclient import TestClient

from document_search_service.app import app


@pytest.fixture()
def client():
    return TestClient(app)