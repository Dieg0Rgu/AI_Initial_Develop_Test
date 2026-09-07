"""
Módulo de Persistencia Relacional (SQLite).

Registra las sesiones de chat, los mensajes intercambiados y los tickets de
escalamiento humano generados por el asistente. Cumple con las normas de
persistencia de datos relacionales (tablas, campos, llaves primarias y
foráneas, relaciones entre entidades).

Esquema:
    sessions          (id PK, user_id, channel, created_at, last_activity_at)
    messages          (id PK, session_id FK -> sessions, role, content,
                       is_escalated, created_at)
    escalation_tickets(id PK, session_id FK -> sessions, intent,
                       contact_reason, status, created_at, updated_at)
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

try:
    from app.config import settings
    from app.utils.logger import logger
except ImportError:
    from backend.app.config import settings
    from backend.app.utils.logger import logger

# ---------------------------------------------------------------------------
# Schema DDL
# ---------------------------------------------------------------------------
SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id               TEXT PRIMARY KEY,
    user_id          TEXT,
    channel          TEXT DEFAULT 'web',
    created_at       TEXT DEFAULT (datetime('now', 'localtime')),
    last_activity_at TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS messages (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id   TEXT NOT NULL,
    role         TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content      TEXT NOT NULL,
    is_escalated INTEGER NOT NULL DEFAULT 0,
    created_at   TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS escalation_tickets (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id     TEXT NOT NULL,
    intent         TEXT NOT NULL,
    contact_reason TEXT,
    status         TEXT NOT NULL DEFAULT 'abierto'
                   CHECK (status IN ('abierto', 'en_proceso', 'cerrado')),
    created_at     TEXT DEFAULT (datetime('now', 'localtime')),
    updated_at     TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_messages_session    ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_tickets_status      ON escalation_tickets(status);
CREATE INDEX IF NOT EXISTS idx_sessions_activity   ON sessions(last_activity_at);

-- Un ticket abierto por (sesión, intención): evita duplicados en la cola.
DELETE FROM escalation_tickets
WHERE id NOT IN (SELECT MIN(id) FROM escalation_tickets GROUP BY session_id, intent);
CREATE UNIQUE INDEX IF NOT EXISTS idx_tickets_session_intent
    ON escalation_tickets(session_id, intent);
"""

TICKET_STATUSES = ("abierto", "en_proceso", "cerrado")


def get_db_path() -> Path:
    return Path(settings.DB_PATH)


@contextmanager
def _connect() -> Iterator[sqlite3.Connection]:
    """Abre una conexión, hace commit/rollback al salir y SIEMPRE la cierra.

    Nota: `with sqlite3.connect(...) as conn:` NO cierra la conexión; en Windows
    el archivo queda bloqueado hasta el garbage collector.
    """
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), timeout=15)
    try:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        with conn:  # transaccional: commit al salir, rollback ante excepción
            yield conn
    finally:
        conn.close()


def init_db() -> None:
    """Creates the relational schema if it does not exist yet."""
    try:
        with _connect() as conn:
            conn.executescript(SCHEMA)
            conn.commit()
        logger.info(f"SQLite persistence initialized at {get_db_path()}")
    except Exception as exc:  # pragma: no cover - defensive in serverless
        logger.warning(f"[WARNING] Persistence init skipped: {exc}")


def _safe(fn):
    """Best-effort wrapper: persistence must never break the chat flow."""
    try:
        return fn()
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning(f"[WARNING] Persistence operation failed: {exc}")
        return None


def upsert_session(session_id: str, channel: str = "web", user_id: Optional[str] = None) -> None:
    """Creates the session on first message or refreshes its activity timestamp."""
    def _run():
        with _connect() as conn:
            conn.execute(
                """
                INSERT INTO sessions (id, channel, user_id, last_activity_at)
                VALUES (?, ?, ?, datetime('now', 'localtime'))
                ON CONFLICT(id) DO UPDATE SET
                    last_activity_at = datetime('now', 'localtime'),
                    channel = excluded.channel,
                    user_id = COALESCE(excluded.user_id, sessions.user_id)
                """,
                (session_id, channel, user_id),
            )
            conn.commit()
    _safe(_run)


def record_message(
    session_id: str, role: str, content: str, is_escalated: bool = False
) -> Optional[int]:
    """Persists one chat message and returns its id."""
    def _run():
        with _connect() as conn:
            cur = conn.execute(
                "INSERT INTO messages (session_id, role, content, is_escalated) VALUES (?, ?, ?, ?)",
                (session_id, role, content, 1 if is_escalated else 0),
            )
            conn.execute(
                "UPDATE sessions SET last_activity_at = datetime('now', 'localtime') WHERE id = ?",
                (session_id,),
            )
            conn.commit()
            return cur.lastrowid
    return _safe(_run)


def record_escalation_ticket(
    session_id: str, intent: str, contact_reason: Optional[str] = None
) -> None:
    """
    Opens (or reopens) an escalation ticket for the given session + intent.
    A single open ticket per session avoids flooding the human queue.
    """
    def _run():
        with _connect() as conn:
            conn.execute(
                """
                INSERT INTO escalation_tickets (session_id, intent, contact_reason, status)
                VALUES (?, ?, ?, 'abierto')
                ON CONFLICT(session_id, intent) DO UPDATE SET
                    contact_reason = COALESCE(excluded.contact_reason, escalation_tickets.contact_reason),
                    status = CASE WHEN escalation_tickets.status = 'cerrado'
                                  THEN 'abierto' ELSE escalation_tickets.status END,
                    updated_at = datetime('now', 'localtime')
                """,
                (session_id, intent, contact_reason),
            )
            conn.commit()
    _safe(_run)


def list_sessions(limit: int = 30) -> List[Dict[str, Any]]:
    """Returns recent sessions with message counts for the history view."""
    def _run():
        with _connect() as conn:
            rows = conn.execute(
                """
                SELECT s.id,
                       s.channel,
                       s.user_id,
                       s.created_at,
                       s.last_activity_at,
                       COUNT(m.id)                                     AS message_count,
                       SUM(CASE WHEN m.is_escalated = 1 THEN 1 ELSE 0 END) AS escalated_count,
                       (SELECT content FROM messages m2
                         WHERE m2.session_id = s.id
                         ORDER BY m2.id DESC LIMIT 1)                  AS last_message
                FROM sessions s
                LEFT JOIN messages m ON m.session_id = s.id
                GROUP BY s.id
                ORDER BY s.last_activity_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]
    result = _safe(_run)
    return result or []


def get_session_messages(session_id: str) -> List[Dict[str, Any]]:
    """Returns the full transcript of a session."""
    def _run():
        with _connect() as conn:
            rows = conn.execute(
                """
                SELECT id, session_id, role, content, is_escalated, created_at
                FROM messages
                WHERE session_id = ?
                ORDER BY id ASC
                """,
                (session_id,),
            ).fetchall()
            return [dict(r) for r in rows]
    result = _safe(_run)
    return result or []


def list_tickets(status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Lists escalation tickets, optionally filtered by status."""
    def _run():
        with _connect() as conn:
            if status:
                rows = conn.execute(
                    """
                    SELECT t.id, t.session_id, t.intent, t.contact_reason,
                           t.status, t.created_at, t.updated_at,
                           s.channel
                    FROM escalation_tickets t
                    LEFT JOIN sessions s ON s.id = t.session_id
                    WHERE t.status = ?
                    ORDER BY t.created_at DESC
                    """,
                    (status,),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT t.id, t.session_id, t.intent, t.contact_reason,
                           t.status, t.created_at, t.updated_at,
                           s.channel
                    FROM escalation_tickets t
                    LEFT JOIN sessions s ON s.id = t.session_id
                    ORDER BY t.created_at DESC
                    """
                ).fetchall()
            return [dict(r) for r in rows]
    result = _safe(_run)
    return result or []


def update_ticket_status(ticket_id: int, status: str) -> Optional[Dict[str, Any]]:
    """Transitions a ticket between 'abierto', 'en_proceso' and 'cerrado'."""
    if status not in TICKET_STATUSES:
        raise ValueError(f"Invalid ticket status '{status}'. Use one of {TICKET_STATUSES}.")

    def _run():
        with _connect() as conn:
            conn.execute(
                """
                UPDATE escalation_tickets
                SET status = ?, updated_at = datetime('now', 'localtime')
                WHERE id = ?
                """,
                (status, ticket_id),
            )
            conn.commit()
            row = conn.execute(
                "SELECT * FROM escalation_tickets WHERE id = ?", (ticket_id,)
            ).fetchone()
            return dict(row) if row else None
    return _safe(_run)
