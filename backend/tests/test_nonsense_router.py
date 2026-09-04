import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.routers.nonsense import check_out_of_scope


def test_check_out_of_scope_historical():
    is_oos, msg = check_out_of_scope("¿Quién fue Adolf Hitler?", language="es")
    assert is_oos is True
    assert "Fuera de Alcance" in msg or "histórica" in msg

    is_oos_en, msg_en = check_out_of_scope("Who was Napoleon?", language="en")
    assert is_oos_en is True
    assert "Out-of-Scope" in msg_en


def test_check_out_of_scope_recipe():
    is_oos, msg = check_out_of_scope("Pásame la receta de la lasagna", language="es")
    assert is_oos is True
    assert "Inglés Vocacional Culinario" in msg or "recetas" in msg

    is_oos_en, msg_en = check_out_of_scope("give me the recipe for pizza", language="en")
    assert is_oos_en is True
    assert "Culinary English" in msg_en


def test_check_out_of_scope_tech_and_crypto():
    is_oos, msg = check_out_of_scope("Escribe un script en python para scraping", language="es")
    assert is_oos is True
    assert "Fuera de Ámbito" in msg or "cursos de inglés" in msg

    is_oos_en, msg_en = check_out_of_scope("how to buy bitcoin cryptocurrency", language="en")
    assert is_oos_en is True
    assert "Not Supported" in msg_en


def test_check_in_scope_queries():
    is_oos, msg = check_out_of_scope("¿Cuáles son los precios del curso de inglés?", language="es")
    assert is_oos is False
    assert msg is None


def test_nonsense_router_endpoints():
    client = TestClient(app)

    # 1. GET /api/nonsense
    resp_get = client.get("/api/nonsense")
    assert resp_get.status_code == 200
    data_get = resp_get.json()
    assert data_get["status"] == "active"
    assert "out_of_scope_categories" in data_get
    assert len(data_get["out_of_scope_categories"]) >= 3

    # 2. POST /api/nonsense/check
    resp_post = client.post("/api/nonsense/check", json={
        "query": "¿Quién es Adolf Hitler?",
        "language": "es"
    })
    assert resp_post.status_code == 200
    data_post = resp_post.json()
    assert data_post["is_out_of_scope"] is True
    assert data_post["response_message"] is not None

    # 3. /api/chat intercepts nonsense query
    chat_resp = client.post("/api/chat", json={
        "message": "¿Quién fue Hitler?",
        "session_id": "nonsense_test_sess",
        "language": "es"
    })
    assert chat_resp.status_code == 200
    chat_data = chat_resp.json()
    assert "Fuera de Alcance" in chat_data["response"]
    assert chat_data["is_escalated"] is False
    assert chat_data["cached"] is False

