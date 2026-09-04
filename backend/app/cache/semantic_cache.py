from __future__ import annotations
import time
import math
import re
import unicodedata
from typing import Optional, Dict, Any, List, Tuple

try:
    from app.config import settings
    from app.rag.embeddings import SmartEmbeddingFunction
except ImportError:
    from backend.app.config import settings
    from backend.app.rag.embeddings import SmartEmbeddingFunction

COMMON_SYNONYMS = {
    "cuesta": "precio precios costo costos valor valores inversion",
    "cuestan": "precio precios costo costos valor valores inversion",
    "vale": "precio precios costo costos valor valores inversion",
    "valen": "precio precios costo costos valor valores inversion",
    "precio": "precio precios costo costos valor valores inversion",
    "precios": "precio precios costo costos valor valores inversion",
    "costo": "precio precios costo costos valor valores inversion",
    "costos": "precio precios costo costos valor valores inversion",
    "tarifa": "tarifa tarifas mensualidad mensualidades precio valor",
    "tarifas": "tarifa tarifas mensualidad mensualidades precio valor",
    "horario": "horario horarios jornada jornadas turno turnos",
    "horarios": "horario horarios jornada jornadas turno turnos",
    "sede": "sede sedes campus ubicacion ubicaciones",
    "sedes": "sede sedes campus ubicacion ubicaciones",
    "donde": "donde ubicacion direccion sedes campus",
    "inicio": "inicio inicios fecha fechas comienzo comenzar empezar",
    "inicios": "inicio inicios fecha fechas comienzo comenzar empezar",
}


class SemanticCacheService:
    """
    Semantic Vector Cache using cosine similarity over query embeddings.
    Allows returning pre-generated responses for semantically equivalent queries
    (e.g., 'cuánto cuesta el curso' vs 'precio de las clases'), avoiding LLM invocations.
    """

    def __init__(
        self,
        threshold: Optional[float] = None,
        max_size: Optional[int] = None,
        enabled: Optional[bool] = None,
        ttl_seconds: Optional[int] = None
    ):
        self.threshold = threshold if threshold is not None else getattr(settings, "SEMANTIC_CACHE_THRESHOLD", 0.88)
        self.max_size = max_size if max_size is not None else getattr(settings, "SEMANTIC_CACHE_MAX_SIZE", 500)
        self.enabled = enabled if enabled is not None else getattr(settings, "SEMANTIC_CACHE_ENABLED", True)
        self.ttl = ttl_seconds if ttl_seconds is not None else settings.CACHE_TTL_SECONDS
        self._embedder = SmartEmbeddingFunction()

        # Cache entries: List of Dict containing query, lang, vector, data, timestamp, hit_count
        self._entries: List[Dict[str, Any]] = []
        self.hits: int = 0
        self.misses: int = 0
        self.tokens_saved: int = 0

    def _preprocess_text(self, text: str) -> str:
        nfkd = unicodedata.normalize('NFKD', text)
        clean = "".join([c for c in nfkd if not unicodedata.combining(c)]).lower().strip()
        clean = re.sub(r'[^\w\s]', '', clean)
        words = clean.split()
        expanded = []
        for w in words:
            expanded.append(w)
            if w in COMMON_SYNONYMS:
                expanded.extend(COMMON_SYNONYMS[w].split())
        return " ".join(expanded)

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        if len(vec1) != len(vec2) or not vec1:
            return 0.0
        # Vectors from SmartEmbeddingFunction are unit-normalized; dot product gives cosine similarity
        dot = sum(a * b for a, b in zip(vec1, vec2))
        return max(0.0, min(1.0, dot))

    def _get_vector(self, text: str) -> List[float]:
        prep = self._preprocess_text(text)
        try:
            embeddings = self._embedder([prep])
            if embeddings and len(embeddings) > 0:
                vec = embeddings[0]
                norm = math.sqrt(sum(x * x for x in vec))
                if norm > 0:
                    return [x / norm for x in vec]
                return vec
        except Exception:
            pass
        return self._embedder._fallback_embed(prep)

    def get(self, query: str, language: str = "es") -> Optional[Tuple[Dict[str, Any], float]]:
        """
        Searches semantic cache for a query with similarity >= threshold.
        Returns: (cached_response_dict, similarity_score) or None.
        """
        if not self.enabled or not query.strip() or not self._entries:
            self.misses += 1
            return None

        lang = (language or "es").lower()
        now = time.time()

        # Purge expired entries
        self._entries = [e for e in self._entries if now - e["timestamp"] <= self.ttl]

        query_vec = self._get_vector(query)
        best_entry = None
        best_sim = 0.0

        for entry in self._entries:
            if entry["lang"] != lang:
                continue

            sim = self._cosine_similarity(query_vec, entry["vector"])
            if sim > best_sim:
                best_sim = sim
                best_entry = entry

        if best_entry and best_sim >= self.threshold:
            best_entry["hit_count"] += 1
            best_entry["last_accessed"] = now
            self.hits += 1
            self.tokens_saved += best_entry["data"].get("token_usage", {}).get("total_tokens", 0)
            return best_entry["data"], round(best_sim, 4)

        self.misses += 1
        return None

    def set(self, query: str, language: str, data: Dict[str, Any]):
        """
        Stores query embedding and response in semantic cache.
        Does not store escalated cases or empty queries.
        """
        if not self.enabled or not query.strip() or data.get("is_escalated", False):
            return

        lang = (language or "es").lower()
        now = time.time()

        # Evict oldest entry if max_size reached
        if len(self._entries) >= self.max_size:
            self._entries.sort(key=lambda e: e["last_accessed"])
            self._entries.pop(0)

        vec = self._get_vector(query)
        self._entries.append({
            "query": query,
            "lang": lang,
            "vector": vec,
            "data": data,
            "timestamp": now,
            "last_accessed": now,
            "hit_count": 0
        })

    def clear(self):
        self._entries.clear()
        self.hits = 0
        self.misses = 0
        self.tokens_saved = 0

    def get_stats(self) -> Dict[str, Any]:
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0.0
        return {
            "semantic_cache_size": len(self._entries),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate_pct": round(hit_rate, 2),
            "tokens_saved": self.tokens_saved,
            "threshold": self.threshold,
            "enabled": self.enabled
        }


# Global singleton
semantic_cache = SemanticCacheService()
