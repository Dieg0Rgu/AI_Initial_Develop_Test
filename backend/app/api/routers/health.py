from __future__ import annotations
from typing import Dict, Any
from fastapi import APIRouter

try:
    from app.rag.vector_store import ChromaVectorStore
    from app.llm.client import OllamaClient
    from app.config import settings
except ImportError:
    from backend.app.rag.vector_store import ChromaVectorStore
    from backend.app.llm.client import OllamaClient
    from backend.app.config import settings

router = APIRouter(prefix="/api/health", tags=["Health"])

_vector_store = ChromaVectorStore()
_llm_client = OllamaClient()

@router.get("")
async def health_check() -> Dict[str, Any]:
    """
    Returns system health, database readiness, and LLM connectivity status.
    """
    ollama_ok = await _llm_client.is_healthy()
    chunks_count = _vector_store.count()

    return {
        "status": "healthy",
        "service": "Gastroteacher AI Customer Support Assistant",
        "environment": settings.ENVIRONMENT,
        "chromadb": {
            "status": "connected",
            "indexed_chunks": chunks_count,
            "ready": chunks_count > 0
        },
        "ollama": {
            "model": settings.OLLAMA_MODEL,
            "base_url": settings.OLLAMA_BASE_URL,
            "connected": ollama_ok
        }
    }
