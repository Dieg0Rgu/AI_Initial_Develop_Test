from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Gastroteacher AI Assistant Backend"
    assert data["status"] == "operational"


def test_chat_get_endpoint_guide():
    response = client.get("/api/chat")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["method_required"] == "POST"


def test_chat_post_endpoint_valid_academic_query():
    payload = {
        "message": "¿Cuáles son los horarios de clases?",
        "session_id": "test_cmd_session",
        "bypass_cache": True,
        "language": "es"
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["is_escalated"] is False
    assert data["cached"] is False
    assert data["latency_ms"] >= 0


def test_chat_post_endpoint_bilingual_english():
    payload = {
        "message": "What are the available schedules and programs?",
        "session_id": "test_en_session",
        "bypass_cache": True,
        "language": "en"
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["is_escalated"] is False


def test_webhook_get_endpoint_guide():
    response = client.get("/api/webhook")
    assert response.status_code == 200
    data = response.json()
    assert data["endpoint"] == "/api/webhook"
    assert data["method_required"] == "POST"


def test_webhook_post_endpoint():
    payload = {
        "message": "Hola, ¿cuándo inician clases?",
        "sender_id": "telegram_test_99",
        "channel": "telegram",
        "metadata": {"language": "es"}
    }
    response = client.post("/api/webhook", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "session_id" in data


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "chromadb" in data


def test_metrics_endpoint_lifecycle():
    # 1. Fetch metrics
    res_get = client.get("/api/metrics")
    assert res_get.status_code == 200
    data = res_get.json()
    assert "total_queries" in data
    assert "performance" in data

    # 2. Reset metrics
    res_reset = client.post("/api/metrics/reset")
    assert res_reset.status_code == 200
    reset_data = res_reset.json()
    assert reset_data["status"] == "success"

    # 3. Verify metrics are 0 after reset
    res_get_after = client.get("/api/metrics")
    assert res_get_after.json()["total_queries"] == 0


def test_documents_status_endpoint():
    response = client.get("/api/documents/status")
    assert response.status_code == 200
    data = response.json()
    assert "total_documents" in data
    assert data["total_documents"] >= 3
