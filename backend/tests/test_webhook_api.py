import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.routers.documents import ingest_all_documents

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def init_db():
    ingest_all_documents()

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Gastroteacher AI Assistant Backend"
    assert data["status"] == "operational"

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["chromadb"]["ready"] is True
    assert data["chromadb"]["indexed_chunks"] > 0

def test_chat_endpoint_valid_query():
    response = client.post("/api/chat", json={
        "message": "¿Cuáles son los precios del curso de inglés general?",
        "session_id": "test_session_1",
        "bypass_cache": True
    })
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert len(data["response"]) > 20
    assert data["is_escalated"] is False
    assert len(data["sources"]) > 0
    assert data["token_usage"]["total_tokens"] > 0

def test_chat_endpoint_cached_query():
    # Prime cache
    client.post("/api/chat", json={
        "message": "¿Tienen clases los sábados?",
        "session_id": "test_session_2",
        "bypass_cache": False
    })
    # Second request should be cached
    response = client.post("/api/chat", json={
        "message": "¿Tienen clases los sábados?",
        "session_id": "test_session_2",
        "bypass_cache": False
    })
    assert response.status_code == 200
    data = response.json()
    assert data["cached"] is True

def test_webhook_endpoint():
    response = client.post("/api/webhook", json={
        "message": "Hola, ¿cómo es el proceso de matrícula?",
        "sender_id": "telegram_user_987",
        "channel": "telegram",
        "metadata": {"user_name": "Diego"}
    })
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["session_id"] == "telegram_telegram_user_987"

def test_metrics_endpoint():
    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["total_queries"] > 0
    assert "escalation_rate_pct" in data
    assert "tokens" in data
    assert "costs" in data
