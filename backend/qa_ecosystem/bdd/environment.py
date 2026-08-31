import os
import sys

# Ensure backend root is on Python path
backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

from fastapi.testclient import TestClient
from app.main import app
from app.cache.cache_service import response_cache

def before_all(context):
    """Initializes the FastAPI TestClient before running BDD features."""
    context.client = TestClient(app)

def before_scenario(context, scenario):
    """Reset scenario context before each test."""
    context.last_response = None
    context.last_json = None
