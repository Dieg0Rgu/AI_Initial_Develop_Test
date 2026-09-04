from __future__ import annotations
from typing import Dict, Any, List
from typing import Dict, Any
from fastapi import APIRouter, HTTPException

try:
    from app.rag.loader import DocumentLoader
    from app.rag.chunker import TextChunker
    from app.rag.vector_store import ChromaVectorStore
except ImportError:
    from backend.app.rag.loader import DocumentLoader
    from backend.app.rag.chunker import TextChunker
    from backend.app.rag.vector_store import ChromaVectorStore

router = APIRouter(prefix="/api/documents", tags=["Documents & Ingestion"])

_loader = DocumentLoader()
_chunker = TextChunker()
_vector_store = ChromaVectorStore()

def ingest_all_documents() -> Dict[str, Any]:
    """
    Core function to load, chunk, and index all documents into ChromaDB.
    """
    docs = _loader.load_documents()
    if not docs:
        return {
            "status": "warning",
            "message": "No documents found in documents directory",
            "documents_loaded": 0,
            "chunks_indexed": 0
        }

    chunks = _chunker.chunk_documents(docs)
    _vector_store.reset_collection()
    indexed_count = _vector_store.add_chunks(chunks)

    return {
        "status": "success",
        "message": f"Successfully indexed {len(docs)} documents into {indexed_count} vector chunks.",
        "documents_loaded": len(docs),
        "chunks_indexed": indexed_count,
        "files": [d["metadata"]["source"] for d in docs]
    }

@router.post("/ingest")
async def trigger_ingestion():
    """
    Endpoint to trigger re-indexing of all knowledge base business documents.
    """
    try:
        result = ingest_all_documents()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@router.get("/status")
async def get_documents_status():
    """
    Endpoint to view current documents in knowledge base and ChromaDB chunk count.
    """
    docs = _loader.load_documents()
    return {
        "total_documents": len(docs),
        "total_chunks_in_db": _vector_store.count(),
        "documents": [d["metadata"] for d in docs]
    }
