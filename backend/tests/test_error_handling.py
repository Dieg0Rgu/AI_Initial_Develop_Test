import pytest
import unittest.mock as mock
from fastapi.testclient import TestClient
from app.main import app
from app.llm.client import OllamaClient
from app.rag.retriever import RAGRetriever
from app.exceptions import (
    GastroteacherException,
    OllamaServiceUnavailableError,
    VectorStoreUnavailableError,
    PDFExportException,
    InvalidQueryException
)

client = TestClient(app)


def test_custom_exception_properties():
    exc = GastroteacherException("Custom failure", status_code=418, details={"field": "test"})
    assert exc.message == "Custom failure"
    assert exc.status_code == 418
    assert exc.details["field"] == "test"

    ollama_exc = OllamaServiceUnavailableError()
    assert ollama_exc.status_code == 503

    vs_exc = VectorStoreUnavailableError()
    assert vs_exc.status_code == 503

    pdf_exc = PDFExportException()
    assert pdf_exc.status_code == 500

    query_exc = InvalidQueryException()
    assert query_exc.status_code == 400


@pytest.mark.asyncio
async def test_ollama_outage_graceful_degradation():
    """
    Ensures that when Ollama raises connection refused or times out,
    the client gracefully uses the deterministic grounded fallback without crashing.
    """
    ollama = OllamaClient()
    with mock.patch("httpx.AsyncClient.post", side_effect=Exception("Connection refused")):
        resp, is_esc, tokens, latency = await ollama.generate_response(
            query="¿Cuáles son los precios?",
            context="Cursos de inglés valen 1.450.000 COP",
            is_relevant=True,
            language="es"
        )

        assert "1.450.000" in resp or "precios" in resp.lower()
        assert is_esc is False
        assert tokens["total_tokens"] > 0
        assert latency >= 0


def test_chromadb_query_failure_graceful_recovery():
    """
    Ensures that when ChromaDB query throws an unexpected error,
    the retriever catches it and returns empty results safely.
    """
    mock_vs = mock.MagicMock()
    mock_vs.query.side_effect = Exception("ChromaDB socket disconnected")

    retriever = RAGRetriever(vector_store=mock_vs)
    chunks, is_relevant, context = retriever.retrieve("¿Precios?")

    assert chunks == []
    assert is_relevant is False
    assert context == ""


def test_pdf_export_invalid_empty_messages():
    """
    Ensures 400 Bad Request is returned when attempting to export an empty chat history.
    """
    response = client.post("/api/export/chat-pdf", json={"session_id": "s1", "messages": []})
    assert response.status_code == 400
    assert "No messages provided" in response.json()["detail"]


def test_pdf_export_nonexistent_document():
    """
    Ensures 404 Not Found is returned when requesting a non-existent PDF file.
    """
    response = client.get("/api/export/documents/non_existent_document_9999.pdf")
    assert response.status_code == 404
