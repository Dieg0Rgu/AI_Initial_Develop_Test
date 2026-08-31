from __future__ import annotations
import time
from typing import List, Dict, Any, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

try:
    from app.rag.retriever import RAGRetriever
    from app.llm.client import OllamaClient
    from app.cache.cache_service import response_cache
    from app.metrics.metrics_tracker import metrics_tracker
except ImportError:
    from backend.app.rag.retriever import RAGRetriever
    from backend.app.llm.client import OllamaClient
    from backend.app.cache.cache_service import response_cache
    from backend.app.metrics.metrics_tracker import metrics_tracker

router = APIRouter(prefix="/api", tags=["Chat & Webhook"])

# Dependency singletons
_retriever = RAGRetriever()
_llm_client = OllamaClient()

class SourceDocument(BaseModel):
    id: str
    source: str
    title: str
    category: str
    similarity_score: float
    excerpt: str

class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Pregunta o consulta del usuario")
    session_id: Optional[str] = Field("default_session", description="ID de sesión del usuario")
    bypass_cache: Optional[bool] = Field(False, description="Forzar respuesta fresca omitiendo la caché")

class WebhookPayload(BaseModel):
    message: str = Field(..., min_length=1, description="Texto del mensaje entrante")
    sender_id: Optional[str] = Field("external_user", description="Identificador del remitente (Telegram ID, email, etc.)")
    channel: Optional[str] = Field("webhook", description="Canal de origen (telegram, email, form, bot)")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadatos adicionales del canal")

class ChatResponse(BaseModel):
    response: str
    is_escalated: bool
    cached: bool
    sources: List[SourceDocument]
    token_usage: TokenUsage
    latency_ms: float
    session_id: str

@router.post("/chat", response_model=ChatResponse)
async def process_chat(request: ChatRequest):
    """
    Main endpoint to process user queries with RAG, caching and human escalation.
    """
    start_total = time.perf_counter()
    query = request.message.strip()

    # 1. Check cache if not bypassed
    if not request.bypass_cache:
        cached_result = response_cache.get(query)
        if cached_result:
            latency_ms = round((time.perf_counter() - start_total) * 1000, 2)
            metrics_tracker.record_query(
                is_escalated=cached_result["is_escalated"],
                prompt_tokens=0,
                completion_tokens=0,
                latency_ms=latency_ms
            )
            return ChatResponse(
                response=cached_result["response"],
                is_escalated=cached_result["is_escalated"],
                cached=True,
                sources=cached_result["sources"],
                token_usage=TokenUsage(**cached_result["token_usage"]),
                latency_ms=latency_ms,
                session_id=request.session_id
            )

    # 2. Retrieve relevant chunks from ChromaDB
    chunks, is_relevant, context = _retriever.retrieve(query)

    # 3. Format sources
    formatted_sources = [
        SourceDocument(
            id=c["id"],
            source=c["source"],
            title=c["title"],
            category=c["category"],
            similarity_score=c["similarity_score"],
            excerpt=c["text"][:220] + ("..." if len(c["text"]) > 220 else "")
        )
        for c in chunks
    ]

    # 4. Generate answer with Ollama (or fallback)
    response_text, is_escalated, token_usage, llm_latency = await _llm_client.generate_response(
        query=query,
        context=context,
        is_relevant=is_relevant
    )

    total_latency_ms = round((time.perf_counter() - start_total) * 1000, 2)

    response_data = {
        "response": response_text,
        "is_escalated": is_escalated,
        "sources": [s.model_dump() for s in formatted_sources],
        "token_usage": token_usage,
        "latency_ms": total_latency_ms
    }

    # 5. Store in cache if not an escalated error
    if not is_escalated:
        response_cache.set(query, response_data)

    # 6. Record metrics
    metrics_tracker.record_query(
        is_escalated=is_escalated,
        prompt_tokens=token_usage.get("prompt_tokens", 0),
        completion_tokens=token_usage.get("completion_tokens", 0),
        latency_ms=total_latency_ms
    )

    return ChatResponse(
        response=response_text,
        is_escalated=is_escalated,
        cached=False,
        sources=formatted_sources,
        token_usage=TokenUsage(**token_usage),
        latency_ms=total_latency_ms,
        session_id=request.session_id
    )

@router.post("/webhook", response_model=ChatResponse)
async def process_webhook(payload: WebhookPayload):
    """
    Webhook endpoint to receive automated messages from Telegram bots, web forms or n8n triggers.
    """
    chat_req = ChatRequest(
        message=payload.message,
        session_id=f"{payload.channel}_{payload.sender_id}",
        bypass_cache=False
    )
    return await process_chat(chat_req)
