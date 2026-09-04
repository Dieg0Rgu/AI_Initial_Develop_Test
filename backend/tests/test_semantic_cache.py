import pytest
from app.cache.semantic_cache import SemanticCacheService, semantic_cache


def test_semantic_cache_basic_set_get():
    cache = SemanticCacheService(threshold=0.85, max_size=10, enabled=True)
    cache.clear()

    payload = {
        "response": "El curso de inglés cuesta 1.450.000 COP",
        "is_escalated": False,
        "sources": [],
        "token_usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        "latency_ms": 150.0
    }

    # Set in cache
    cache.set("¿Cuánto cuesta el curso de inglés?", "es", payload)
    assert cache.get_stats()["semantic_cache_size"] == 1

    # Exact query hit
    res_exact = cache.get("¿Cuánto cuesta el curso de inglés?", "es")
    assert res_exact is not None
    data_exact, sim_exact = res_exact
    assert data_exact["response"] == payload["response"]
    assert sim_exact >= 0.95

    # Very similar query hit
    res_similar = cache.get("cuanto vale el curso de ingles", "es")
    assert res_similar is not None
    data_sim, sim_val = res_similar
    assert data_sim["response"] == payload["response"]
    assert sim_val >= 0.85


def test_semantic_cache_dissimilar_query_miss():
    cache = SemanticCacheService(threshold=0.88, max_size=10, enabled=True)
    cache.clear()

    payload = {
        "response": "Los horarios son de lunes a jueves",
        "is_escalated": False,
        "sources": [],
        "token_usage": {"total_tokens": 20},
        "latency_ms": 50.0
    }
    cache.set("¿Cuáles son los horarios de clase?", "es", payload)

    # Completely different question should miss
    res_diff = cache.get("¿Dónde queda la sede de Medellín?", "es")
    assert res_diff is None


def test_semantic_cache_language_isolation():
    cache = SemanticCacheService(threshold=0.85, max_size=10, enabled=True)
    cache.clear()

    payload_es = {"response": "Respuesta en español", "is_escalated": False}
    cache.set("precios del curso", "es", payload_es)

    # Query in english should not match spanish entry
    res_en = cache.get("precios del curso", "en")
    assert res_en is None


def test_semantic_cache_does_not_store_escalated():
    cache = SemanticCacheService(threshold=0.85, max_size=10, enabled=True)
    cache.clear()

    payload_esc = {"response": "Contacte a soporte", "is_escalated": True}
    cache.set("quiero hablar con un humano", "es", payload_esc)
    assert cache.get_stats()["semantic_cache_size"] == 0


def test_semantic_cache_eviction_and_clear():
    cache = SemanticCacheService(threshold=0.85, max_size=2, enabled=True)
    cache.clear()

    cache.set("pregunta 1", "es", {"response": "resp 1", "is_escalated": False})
    cache.set("pregunta 2", "es", {"response": "resp 2", "is_escalated": False})
    cache.set("pregunta 3", "es", {"response": "resp 3", "is_escalated": False})

    stats = cache.get_stats()
    assert stats["semantic_cache_size"] <= 2
    assert stats["enabled"] is True

    cache.clear()
    assert cache.get_stats()["semantic_cache_size"] == 0
    assert cache.get("pregunta 1", "es") is None

