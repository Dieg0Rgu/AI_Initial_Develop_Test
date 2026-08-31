import pytest
from app.config import settings
from app.llm.prompts import build_rag_prompt
from app.rag.loader import DocumentLoader
from app.rag.chunker import TextChunker
from app.metrics.metrics_tracker import metrics_tracker
from app.cache.cache_service import response_cache
from app.rag.embeddings import SmartEmbeddingFunction
from app.rag.vector_store import ChromaVectorStore
from app.api.routers.documents import trigger_ingestion, get_documents_status
from app.api.routers.health import health_check
from app.api.routers.export import list_official_documents_pdf, download_official_document_pdf, export_chat_pdf, ChatExportRequest
from app.utils.sweet_alert_console import SweetAlert
from app.utils.pdf_generator import GastroteacherPDFGenerator

def test_config_defaults():
    assert settings.PORT == 8000
    assert settings.SIMILARITY_THRESHOLD == 0.45
    assert settings.ESCALATION_EMAIL == "edig0rgudevia@gmail.com"
    assert settings.CACHE_ENABLED is True
    assert settings.MAX_CACHE_SIZE > 0

def test_build_rag_prompt_bilingual():
    prompt_es = build_rag_prompt("¿Cuáles son los precios?", "Contexto oficial de precios", "es")
    assert len(prompt_es) == 2
    assert "Gastroteacher" in prompt_es[0]["content"]

    prompt_en = build_rag_prompt("What are the prices?", "Official pricing context", "en")
    assert len(prompt_en) == 2
    assert "Gastroteacher" in prompt_en[0]["content"]

def test_document_loader_methods():
    loader = DocumentLoader()
    docs = loader.load_documents()
    assert len(docs) >= 3
    for d in docs:
        assert "title" in d["metadata"]
        assert len(d["content"]) > 100

def test_chunker_edge_cases():
    chunker = TextChunker(chunk_size=100, chunk_overlap=20)
    chunks = chunker.split_text("Short text")
    assert len(chunks) == 1
    assert chunks[0] == "Short text"

    # Chunk with multiple lines using chunk_documents
    multiline = "# Title\n\nParagraph 1.\n\nParagraph 2 with extra information."
    chunks_multi = chunker.chunk_documents([{"content": multiline, "metadata": {"source": "test.md", "title": "Test"}}])
    assert len(chunks_multi) >= 1
    assert "metadata" in chunks_multi[0]

def test_embeddings_and_vector_store():
    embedder = SmartEmbeddingFunction()
    # Test embedding call
    emb = embedder(["Test phrase for embedding"])
    assert len(emb) == 1
    assert len(emb[0]) == 384

    config = embedder.get_config()
    assert "model" in config
    assert SmartEmbeddingFunction.name() == "smart_embedding_function"

    vs = ChromaVectorStore()
    assert vs.count() >= 0

@pytest.mark.asyncio
async def test_health_check_endpoint():
    res = await health_check()
    assert res["status"] == "healthy"
    assert "chromadb" in res

@pytest.mark.asyncio
async def test_documents_router_endpoints():
    status = await get_documents_status()
    assert "total_documents" in status
    assert status["total_documents"] >= 3

    ingest_res = await trigger_ingestion()
    assert ingest_res["status"] == "success"

def test_metrics_tracker_and_cache_operations():
    # Record queries
    metrics_tracker.record_query(is_escalated=False, prompt_tokens=100, completion_tokens=50, latency_ms=12.5)
    metrics_tracker.record_query(is_escalated=True, prompt_tokens=80, completion_tokens=40, latency_ms=15.0)

    summary = metrics_tracker.get_summary()
    assert summary["total_queries"] >= 2
    assert summary["escalation_rate_pct"] >= 0.0

    # Cache operations
    response_cache.set("test_key", {"response": "test_answer", "token_usage": {"total_tokens": 50}})
    val = response_cache.get("test_key")
    assert val["response"] == "test_answer"
    stats = response_cache.get_stats()
    assert stats["hits"] >= 1

    # Clear and verify
    response_cache.clear()
    assert response_cache.get("test_key") is None

@pytest.mark.asyncio
async def test_export_router_and_pdf_generation(tmp_path):
    # Official docs list
    docs_res = await list_official_documents_pdf()
    assert docs_res["status"] == "success"
    assert len(docs_res["documents"]) >= 3

    # Generate test chat PDF
    chat_req = ChatExportRequest(
        session_id="test_qa_session",
        messages=[
            {"role": "user", "content": "¿Precios de inglés?", "timestamp": "10:00"},
            {"role": "assistant", "content": "El valor es $1.450.000 COP", "timestamp": "10:01", "sources": [{"source": "02_pricing.md"}]}
        ]
    )
    pdf_resp = await export_chat_pdf(chat_req)
    assert pdf_resp.status_code == 200
    assert pdf_resp.media_type == "application/pdf"

    # Download official doc
    doc_resp = await download_official_document_pdf("01_courses_modalities_levels.pdf")
    assert doc_resp.status_code == 200

    # Direct PDF utils
    pdf_gen = GastroteacherPDFGenerator()
    out_pdf = str(tmp_path / "chat_test.pdf")
    pdf_gen.convert_conversation_to_pdf([{"role": "user", "content": "test"}], "session_1", out_pdf)
    assert tmp_path.joinpath("chat_test.pdf").exists()

def test_sweet_alert_console_rendering():
    SweetAlert.success("Test Success", "All checks passed", {"Total": 10})
    SweetAlert.info("Test Info", "Info text", {"Module": "QA"})
    SweetAlert.warning("Test Warning", "Warning text", {"Issue": "Low RAM"})
    SweetAlert.error("Test Error", "Error text", {"Code": 500})
    SweetAlert.render_summary_table("Summary", ["Col 1", "Col 2"], [["Val 1", "Val 2"]])
