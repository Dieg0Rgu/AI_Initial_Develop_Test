from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

try:
    from app.db import (
        list_sessions,
        get_session_messages,
        list_tickets,
        update_ticket_status,
    )
    from app.db.database import TICKET_STATUSES
except ImportError:
    from backend.app.db import (
        list_sessions,
        get_session_messages,
        list_tickets,
        update_ticket_status,
    )
    from backend.app.db.database import TICKET_STATUSES

router = APIRouter(prefix="/api", tags=["Persistencia, Historial & Tickets"])


class TicketStatusUpdate(BaseModel):
    status: str = Field(..., description="Nuevo estado del ticket: abierto, en_proceso o cerrado")


@router.get("/history")
async def get_history(limit: int = Query(30, ge=1, le=100)) -> Dict[str, Any]:
    """
    Returns the most recent chat sessions with message counts and last activity,
    so the user can browse past conversations.
    """
    sessions = list_sessions(limit=limit)
    return {"status": "success", "total_sessions": len(sessions), "sessions": sessions}


@router.get("/history/{session_id}")
async def get_history_session(session_id: str) -> Dict[str, Any]:
    """
    Returns the full transcript of a single session.
    """
    messages = get_session_messages(session_id)
    if not messages:
        raise HTTPException(status_code=404, detail=f"No se encontró la sesión '{session_id}'.")
    return {"status": "success", "session_id": session_id, "messages": messages}


@router.get("/tickets")
async def get_tickets(
    status: Optional[str] = Query(None, description="Filtrar por estado: abierto, en_proceso, cerrado"),
) -> Dict[str, Any]:
    """
    Lists human escalation tickets for the advisor queue.
    """
    if status is not None and status not in TICKET_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Estado inválido '{status}'. Use uno de {list(TICKET_STATUSES)}.",
        )
    tickets = list_tickets(status=status)
    return {"status": "success", "total_tickets": len(tickets), "tickets": tickets}


@router.patch("/tickets/{ticket_id}")
async def patch_ticket(ticket_id: int, payload: TicketStatusUpdate) -> Dict[str, Any]:
    """
    Updates a ticket status (abierto -> en_proceso -> cerrado).
    """
    try:
        updated = update_ticket_status(ticket_id, payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if updated is None:
        raise HTTPException(status_code=404, detail=f"Ticket '{ticket_id}' no encontrado.")
    return {"status": "success", "ticket": updated}
