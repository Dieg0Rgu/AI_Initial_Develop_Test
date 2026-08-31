import pytest
import asyncio
from app.rag.retriever import RAGRetriever
from app.llm.client import OllamaClient
from app.config import settings
from app.api.routers.documents import ingest_all_documents

@pytest.fixture(scope="module", autouse=True)
def setup_knowledge():
    ingest_all_documents()

@pytest.mark.asyncio
async def test_escalation_on_unrelated_query():
    retriever = RAGRetriever()
    llm = OllamaClient()

    query = "¿Cómo reparar el carburador de una motocicleta Yamaha?"
    chunks, is_relevant, context = retriever.retrieve(query)

    response_text, is_escalated, tokens, latency = await llm.generate_response(query, context, is_relevant=False)

    assert is_escalated is True
    assert (settings.ESCALATION_EMAIL in response_text) or (settings.ESCALATION_WHATSAPP in response_text) or ("asesor" in response_text.lower()) or ("humano" in response_text.lower())

@pytest.mark.asyncio
async def test_escalation_on_crypto_query():
    retriever = RAGRetriever()
    llm = OllamaClient()

    query = "¿Ustedes aceptan pagos en Bitcoin y dan cursos de trading de criptomonedas?"
    chunks, is_relevant, context = retriever.retrieve(query)

    response_text, is_escalated, tokens, latency = await llm.generate_response(query, context, is_relevant=False)

    assert is_escalated is True
    assert ("soporte" in response_text.lower()) or ("asesor" in response_text.lower()) or ("escalado" in response_text.lower())
