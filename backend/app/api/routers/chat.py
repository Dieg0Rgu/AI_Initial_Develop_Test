from __future__ import annotations
import time
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

try:
    from app.config import settings
    from app.rag.retriever import RAGRetriever
    from app.llm.client import (
        OllamaClient,
        normalize_simple,
        contains_profanity,
        is_gibberish,
        extract_name_intent,
        has_exact_keyword,
        GREETING_WORDS,
        NONSENSE_KEYWORDS,
        IN_SCOPE_KEYWORDS
    )
    from app.cache.cache_service import response_cache
    from app.metrics.metrics_tracker import metrics_tracker
except ImportError:
    from backend.app.config import settings
    from backend.app.rag.retriever import RAGRetriever
    from backend.app.llm.client import (
        OllamaClient,
        normalize_simple,
        contains_profanity,
        is_gibberish,
        extract_name_intent,
        has_exact_keyword,
        GREETING_WORDS,
        NONSENSE_KEYWORDS,
        IN_SCOPE_KEYWORDS
    )
    from backend.app.cache.cache_service import response_cache
    from backend.app.metrics.metrics_tracker import metrics_tracker

router = APIRouter(prefix="/api", tags=["Chat & RAG"])

_retriever = RAGRetriever()
_llm_client = OllamaClient()

class ChatRequest(BaseModel):
    message: str = Field(..., description="Pregunta o consulta del usuario")
    session_id: Optional[str] = Field("default_session", description="ID de sesión de chat")
    bypass_cache: Optional[bool] = Field(False, description="Forzar respuesta fresca omitiendo la memoria caché")
    language: Optional[str] = Field("es", description="Idioma de la interfaz y respuesta ('es' o 'en')")

class WebhookPayload(BaseModel):
    message: str = Field(..., description="Mensaje entrante del webhook")
    sender_id: str = Field(..., description="ID del remitente")
    channel: Optional[str] = Field("telegram", description="Canal de origen (telegram, web, n8n)")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadatos adicionales")

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

class ChatResponse(BaseModel):
    response: str
    is_escalated: bool
    cached: bool
    sources: List[SourceDocument]
    token_usage: TokenUsage
    latency_ms: float
    session_id: str

@router.get("/chat")
async def chat_info():
    """
    Informative guide for GET requests in the browser.
    """
    return {
        "status": "online",
        "endpoint": "/api/chat",
        "method_required": "POST",
        "description": "Este endpoint recibe consultas mediante POST con payload JSON.",
        "example_payload": {
            "message": "¿Cuáles son los precios del curso de inglés?",
            "session_id": "mi_sesion_123",
            "bypass_cache": False,
            "language": "es"
        },
        "swagger_docs": "http://localhost:8000/docs",
        "frontend_app": "http://localhost:5173"
    }

@router.post("/chat", response_model=ChatResponse)
async def process_chat(request: ChatRequest):
    """
    Main endpoint to process user queries with RAG, caching and human escalation.
    """
    start_total = time.perf_counter()
    query = request.message.strip()
    norm_q = normalize_simple(query)
    words = norm_q.split()
    lang = (request.language or "es").lower()

    detected_name = extract_name_intent(query)
    has_vulgarity = contains_profanity(query)
    gibberish = is_gibberish(query)
    has_academic_intent = has_exact_keyword(words, IN_SCOPE_KEYWORDS)

    is_greeting = norm_q in GREETING_WORDS or (len(words) <= 2 and any(w in GREETING_WORDS for w in words) and not has_academic_intent and not has_vulgarity and not gibberish)
    is_isolated_nonsense = (
        not norm_q
        or not any(c.isalnum() for c in query)
        or has_vulgarity
        or gibberish
        or (len(words) <= 2 and (norm_q in NONSENSE_KEYWORDS or any(w in NONSENSE_KEYWORDS for w in words)))
        or (len(words) == 1 and not detected_name and not has_academic_intent)
    ) and not has_academic_intent and not detected_name

    cache_key = f"{lang}:{query}"

    # 1. Check cache if not bypassed
    if not request.bypass_cache:
        cached_result = response_cache.get(cache_key)
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
    if is_greeting or is_isolated_nonsense or detected_name or has_vulgarity or gibberish:
        chunks, is_relevant, context = [], False, ""
    else:
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
        is_relevant=is_relevant,
        language=lang
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
        response_cache.set(cache_key, response_data)

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

@router.get("/webhook")
async def webhook_info():
    """
    Informative guide for GET requests to webhook in the browser.
    """
    return {
        "status": "online",
        "endpoint": "/api/webhook",
        "method_required": "POST",
        "description": "Endpoint de entrada para webhooks de Telegram, n8n o formularios mediante POST.",
        "example_payload": {
            "message": "Hola, ¿cuándo inician clases?",
            "sender_id": "telegram_user_456",
            "channel": "telegram"
        }
    }

@router.post("/webhook", response_model=ChatResponse)
async def process_webhook(payload: WebhookPayload):
    """
    Webhook endpoint to receive automated messages from Telegram bots, web forms or n8n triggers.
    """
    lang = payload.metadata.get("language", "es") if payload.metadata else "es"
    chat_req = ChatRequest(
        message=payload.message,
        session_id=f"{payload.channel}_{payload.sender_id}",
        bypass_cache=False,
        language=lang
    )
    return await process_chat(chat_req)
