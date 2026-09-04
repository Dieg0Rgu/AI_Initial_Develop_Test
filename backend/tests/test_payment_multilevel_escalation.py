from __future__ import annotations
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.cache.faq_service import faq_service

client = TestClient(app)


def test_payment_queries_trigger_level_1_not_immediate_escalation():
    """Verify that natural variations of payment issues trigger Level 1 without escalating."""
    queries = [
        "tengo problema en el pago",
        "tengo un problema para pagar",
        "problema con el pago",
        "error al pagar por PSE",
        "no puedo pagar con tarjeta",
        "falla en la pasarela de pagos",
        "inconveniente con mi pago",
        "no me deja pagar"
    ]

    for i, q in enumerate(queries):
        sid = f"sess_l1_test_{i}"
        faq_service.clear_session(sid)
        res = client.post("/api/chat", json={"message": q, "session_id": sid})
        assert res.status_code == 200
        data = res.json()
        assert data["is_escalated"] is False, f"Query '{q}' escalated immediately to human!"
        assert "Nivel 1" in data["response"] or "pasos de verificación" in data["response"]


def test_payment_three_level_full_progression():
    """Verify Level 1 -> Level 2 -> Level 3 (escalation) strict progression."""
    sid = "sess_full_progression_123"
    faq_service.clear_session(sid)

    # Step 1: Initial query
    r1 = client.post("/api/chat", json={"message": "tengo problema en el pago", "session_id": sid}).json()
    assert r1["is_escalated"] is False
    assert "Nivel 1" in r1["response"]

    # Step 2: User insists
    r2 = client.post("/api/chat", json={"message": "aún tengo el problema", "session_id": sid}).json()
    assert r2["is_escalated"] is False
    assert "Nivel 2" in r2["response"]

    # Step 3: User insists again -> Escalate to human
    r3 = client.post("/api/chat", json={"message": "no pude solucionar", "session_id": sid}).json()
    assert r3["is_escalated"] is True
    assert "Nivel 3" in r3["response"] or "Equipo Humano" in r3["response"]


def test_payment_conversational_followup_progression():
    """Verify progression with realistic conversational expressions like 'sigue sin funcionar' and 'no sirvio'."""
    sid = "sess_conversational_456"
    faq_service.clear_session(sid)

    # Step 1: Initial query
    r1 = client.post("/api/chat", json={"message": "no puedo pagar con mi tarjeta", "session_id": sid}).json()
    assert r1["is_escalated"] is False
    assert "Nivel 1" in r1["response"]

    # Step 2: Conversational followup
    r2 = client.post("/api/chat", json={"message": "sigue sin funcionar", "session_id": sid}).json()
    assert r2["is_escalated"] is False
    assert "Nivel 2" in r2["response"]

    # Step 3: Final insistence -> Escalation
    r3 = client.post("/api/chat", json={"message": "no sirvio", "session_id": sid}).json()
    assert r3["is_escalated"] is True
    assert "Nivel 3" in r3["response"] or "Equipo Humano" in r3["response"]


def test_markdown_table_cleaning_removes_pipes_and_dividers():
    """Verify clean_markdown_response transforms markdown tables into text without pipes or lines."""
    from app.llm.client import clean_markdown_response

    sample_table = (
        "| Modalidad | Rango de precios (COP) |\n"
        "|-----------|------------------------|\n"
        "| Presencial (clases en nuestras sedes de Bogotá o Medellín) | Aproximadamente 1.200.000 – 1.800.000 COP por ciclo (12 semanas). |\n"
        "| Online en vivo (clases 100 % virtuales) | Aproximadamente 1.000.000 – 1.500.000 COP por ciclo (12 semanas). |\n"
        "---\n"
        "Para más información escríbenos."
    )

    cleaned = clean_markdown_response(sample_table)
    assert "|" not in cleaned
    assert "---" not in cleaned
    assert "Presencial" in cleaned
    assert "Online en vivo" in cleaned
    assert "1.200.000" in cleaned


