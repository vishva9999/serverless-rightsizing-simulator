import pytest
from fastapi.testclient import TestClient
import sys
import os

# Ensure backend root is on sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app


@pytest.fixture(scope="session")
def client():
    """Provides a TestClient for making HTTP requests to the FastAPI application."""
    with TestClient(app) as test_client:
        yield test_client
