import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.cache.faq_service import faq_service, normalize_text


def test_normalize_text():
    assert normalize_text("  ¡HÓLA, cómo estás?  ") == "hola como estas"
    assert normalize_text("") == ""


def test_payment_issues_three_level_escalation():
    sess_id = "test_pay_session_1"
    faq_service.clear_session(sess_id)

    # Level 1: Initial report
    res1 = faq_service.match_faq("Tengo un problema con el pago de la matrícula", session_id=sess_id, language="es")
    assert res1 is not None
    text1, esc1 = res1
    assert "Nivel 1" in text1 or "pasos de verificación" in text1
    assert esc1 is False
    assert faq_service.get_session(sess_id)["level"] == 1

    # Level 2: Follow-up saying still have the problem
    res2 = faq_service.match_faq("Aún tengo el problema con la pasarela", session_id=sess_id, language="es")
    assert res2 is not None
    text2, esc2 = res2
    assert "Nivel 2" in text2 or "Wompi" in text2 or "Bancolombia" in text2
    assert esc2 is False
    assert faq_service.get_session(sess_id)["level"] == 2

    # Level 3: Follow-up saying not solved -> Escalate to human
    res3 = faq_service.match_faq("No pude solucionar el inconveniente", session_id=sess_id, language="es")
    assert res3 is not None
    text3, esc3 = res3
    assert esc3 is True
    assert "Tesorería" in text3 or "+57 313 730 1501" in text3
    assert faq_service.get_session(sess_id) is None


def test_payment_issues_english_three_levels():
    sess_id = "test_pay_session_en"
    faq_service.clear_session(sess_id)

    res1 = faq_service.match_faq("I have a payment issue", session_id=sess_id, language="en")
    assert res1 is not None
    assert "Level 1" in res1[0] or "Browser Check" in res1[0]
    assert res1[1] is False

    res2 = faq_service.match_faq("still have the problem", session_id=sess_id, language="en")
    assert res2 is not None
    assert "Level 2" in res2[0] or "Wompi" in res2[0]
    assert res2[1] is False

    res3 = faq_service.match_faq("did not solve", session_id=sess_id, language="en")
    assert res3 is not None
    assert res3[1] is True


def test_registration_issues_escalation():
    sess_id = "test_reg_session"
    faq_service.clear_session(sess_id)

    res1 = faq_service.match_faq("No puedo registrarme en la plataforma", session_id=sess_id, language="es")
    assert res1 is not None
    assert res1[1] is False

    res2 = faq_service.match_faq("aún tengo el problema", session_id=sess_id, language="es")
    assert res2 is not None
    assert res2[1] is True
    assert "Admisiones" in res2[0]


def test_static_faq_matches():
    res_sedes = faq_service.match_faq("¿Dónde están ubicados?", language="es")
    assert res_sedes is not None
    assert "Bogotá" in res_sedes[0] and "Medellín" in res_sedes[0]

    res_sedes_en = faq_service.match_faq("where are your campuses located?", language="en")
    assert res_sedes_en is not None

    res_metodos = faq_service.match_faq("¿Cuáles son los métodos de pago?", language="es")
    assert res_metodos is not None
    assert "PSE" in res_metodos[0]

    res_none = faq_service.match_faq("consulta totalmente desconocida y aleatoria", language="es")
    assert res_none is None


def test_chat_api_integration_with_faq():
    client = TestClient(app)
    sess_id = "api_client_faq_test"

    # Step 1: Trigger level 1 via chat endpoint
    r1 = client.post("/api/chat", json={
        "message": "Tengo un problema para pagar",
        "session_id": sess_id,
        "language": "es"
    })
    assert r1.status_code == 200
    data1 = r1.json()
    assert "Nivel 1" in data1["response"] or "pasos de verificación" in data1["response"]
    assert data1["is_escalated"] is False

    # Step 2: Trigger level 2 via chat endpoint
    r2 = client.post("/api/chat", json={
        "message": "Aún tengo el problema",
        "session_id": sess_id,
        "language": "es"
    })
    assert r2.status_code == 200
    data2 = r2.json()
    assert "Nivel 2" in data2["response"] or "Wompi" in data2["response"]
    assert data2["is_escalated"] is False

    # Step 3: Trigger level 3 via chat endpoint
    r3 = client.post("/api/chat", json={
        "message": "No pude solucionar",
        "session_id": sess_id,
        "language": "es"
    })
    assert r3.status_code == 200
    data3 = r3.json()
    assert data3["is_escalated"] is True

