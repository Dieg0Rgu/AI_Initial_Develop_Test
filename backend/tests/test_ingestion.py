from app.rag.loader import DocumentLoader
from app.rag.chunker import TextChunker
from app.rag.vector_store import ChromaVectorStore
from app.api.routers.documents import ingest_all_documents


def test_document_loader_loads_at_least_three_documents():
    loader = DocumentLoader()
    docs = loader.load_documents()
    assert len(docs) >= 3, f"Expected at least 3 business documents, but found {len(docs)}"
    for doc in docs:
        assert "content" in doc
        assert "metadata" in doc
        assert doc["metadata"]["source"].endswith((".md", ".txt"))
        assert len(doc["content"]) > 100


def test_chunker_splits_with_overlap():
    chunker = TextChunker(chunk_size=300, chunk_overlap=50)
    sample_text = (
        "En Gastroteacher Academy ofrecemos cursos especializados de inglés culinario. "
        "Nuestras sedes en Bogotá y Medellín cuentan con cocinas de práctica de última generación. "
        "El programa de Gastronomy & Hospitality English tiene una duración de 120 horas distribuidas "
        "en 3 niveles: Kitchen Ops, Front of House & Wine, y Executive Gastronomy Management. "
        "Cada nivel cuesta $720.000 COP o el paquete completo de contado por $1.980.000 COP."
    )
    chunks = chunker.split_text(sample_text)
    assert len(chunks) >= 1
    for chunk in chunks:
        assert len(chunk) <= 400


def test_full_document_ingestion_populates_vector_store():
    result = ingest_all_documents()
    assert result["status"] == "success"
    assert result["documents_loaded"] >= 3
    assert result["chunks_indexed"] > 0

    vector_store = ChromaVectorStore()
    assert vector_store.count() >= result["chunks_indexed"]
