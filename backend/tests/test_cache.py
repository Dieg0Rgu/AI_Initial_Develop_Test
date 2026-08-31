import pytest
from app.cache.cache_service import ResponseCacheService

def test_cache_set_and_get():
    cache = ResponseCacheService(ttl_seconds=60, max_size=10, enabled=True)
    cache.clear()

    query = "¿Cuáles son los horarios de atención?"
    payload = {
        "response": "Atendemos de lunes a viernes de 8am a 6pm.",
        "is_escalated": False,
        "sources": [],
        "token_usage": {"prompt_tokens": 50, "completion_tokens": 20, "total_tokens": 70},
        "latency_ms": 120.5
    }

    # Miss on first attempt
    assert cache.get(query) is None

    # Set cache
    cache.set(query, payload)

    # Hit on second attempt
    cached_data = cache.get(query)
    assert cached_data is not None
    assert cached_data["response"] == payload["response"]

    # Hit on normalized variation (casing and punctuation difference)
    normalized_variation = "  cuales son los horarios de atencion? "
    cached_variation = cache.get(normalized_variation)
    assert cached_variation is not None
    assert cached_variation["response"] == payload["response"]

    # Check stats
    stats = cache.get_stats()
    assert stats["hits"] >= 2
    assert stats["tokens_saved"] >= 140
