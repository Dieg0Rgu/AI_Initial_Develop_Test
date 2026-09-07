"""
Tests del Módulo de Persistencia Relacional (SQLite):
- Tablas sessions / messages / escalation_tickets
- CRUD de sesiones, mensajes y tickets
- Endpoints /api/history y /api/tickets
"""
import pytest
from fastapi.testclient import TestClient

from app.db.database import (
    init_db,
    upsert_session,
    record_message,
    record_escalation_ticket,
    list_sessions,
    get_session_messages,
    list_tickets,
    update_ticket_status,
    TICKET_STATUSES,
)


@pytest.fixture()
def temp_db(monkeypatch, tmp_path):
    """Aísla las pruebas en una base SQLite temporal."""
    db_file = tmp_path / "test_persistence.db"
    # El módulo lee la ruta vía get_db_path() en tiempo de ejecución.
    from app.db import database as db_module

    monkeypatch.setattr(db_module, "get_db_path", lambda: db_file)
    init_db()
    yield str(db_file)


def test_schema_created(temp_db):
    """Las tres tablas relacionales existen tras init_db()."""
    import sqlite3

    conn = sqlite3.connect(temp_db)
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    conn.close()
    assert {"sessions", "messages", "escalation_tickets"} <= tables


def test_session_and_messages_roundtrip(temp_db):
    """Se persiste una sesión y sus mensajes correctamente."""
    upsert_session("sesion_a", channel="web")
    m1 = record_message("sesion_a", "user", "¿Cuáles son los precios?")
    m2 = record_message("sesion_a", "assistant", "El nivel cuesta $1.450.000 COP", is_escalated=False)

    assert m1 is not None and m2 is not None
    messages = get_session_messages("sesion_a")
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["is_escalated"] == 0

    sessions = list_sessions()
    assert sessions[0]["id"] == "sesion_a"
    assert sessions[0]["message_count"] == 2


def test_escalation_ticket_lifecycle(temp_db):
    """El ticket se crea abierto y transiciona en_proceso -> cerrado."""
    upsert_session("sesion_refund")
    record_message("sesion_refund", "user", "Exijo la devolución", is_escalated=True)
    record_escalation_ticket("sesion_refund", intent="REFUND", contact_reason="Exijo la devolución")

    tickets = list_tickets()
    assert len(tickets) == 1
    ticket = tickets[0]
    assert ticket["status"] == "abierto"
    assert ticket["intent"] == "REFUND"

    # Transición de estado
    updated = update_ticket_status(ticket["id"], "en_proceso")
    assert updated["status"] == "en_proceso"
    updated = update_ticket_status(ticket["id"], "cerrado")
    assert updated["status"] == "cerrado"

    # Filtro por estado
    assert list_tickets(status="abierto") == []
    assert len(list_tickets(status="cerrado")) == 1


def test_ticket_deduplication_per_session(temp_db):
    """Dos escalamientos de la misma sesión/intención no duplican el ticket abierto."""
    upsert_session("s")
    record_escalation_ticket("s", intent="TECHNICAL", contact_reason="Error 403")
    record_escalation_ticket("s", intent="TECHNICAL", contact_reason="Error 403 de nuevo")
    open_tickets = list_tickets(status="abierto")
    assert len(open_tickets) == 1
    assert open_tickets[0]["contact_reason"] == "Error 403 de nuevo"


def test_update_ticket_invalid_status(temp_db):
    with pytest.raises(ValueError):
        update_ticket_status(1, "inexistente")


def test_update_ticket_not_found(temp_db):
    assert update_ticket_status(9999, "cerrado") is None


def test_history_and_tickets_endpoints(temp_db):
    """Integración: los endpoints expuestos por FastAPI funcionan."""
    upsert_session("sesion_api", channel="web")
    record_message("sesion_api", "user", "¿Horarios de clase?")
    record_message("sesion_api", "assistant", "Lunes a jueves 6:30 AM.")
    record_escalation_ticket("sesion_api", intent="HUMAN", contact_reason="Quiero un asesor")

    from app.main import app

    client = TestClient(app)

    # Historial de sesiones
    res = client.get("/api/history")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert any(s["id"] == "sesion_api" for s in data["sessions"])

    # Transcripción
    res = client.get("/api/history/sesion_api")
    assert res.status_code == 200
    assert len(res.json()["messages"]) == 2

    # 404 en sesión inexistente
    res = client.get("/api/history/no_existe")
    assert res.status_code == 404

    # Bandeja de tickets
    res = client.get("/api/tickets")
    assert res.status_code == 200
    tickets = res.json()["tickets"]
    assert len(tickets) >= 1
    ticket_id = tickets[0]["id"]

    # Actualizar estado del ticket
    res = client.patch(f"/api/tickets/{ticket_id}", json={"status": "en_proceso"})
    assert res.status_code == 200
    assert res.json()["ticket"]["status"] == "en_proceso"

    # Estado inválido
    res = client.patch(f"/api/tickets/{ticket_id}", json={"status": "nope"})
    assert res.status_code == 400


def test_ticket_statuses_enum():
    assert TICKET_STATUSES == ("abierto", "en_proceso", "cerrado")
