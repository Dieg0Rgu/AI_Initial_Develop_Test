from __future__ import annotations
import time
import re
import unicodedata
from typing import Optional, Dict, Any

try:
    from app.config import settings
except ImportError:
    from backend.app.config import settings

class ResponseCacheService:
    def __init__(self, ttl_seconds: int = None, max_size: int = None, enabled: bool = None):
        self.ttl = ttl_seconds or settings.CACHE_TTL_SECONDS
        self.max_size = max_size or settings.MAX_CACHE_SIZE
        self.enabled = enabled if enabled is not None else settings.CACHE_ENABLED
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.hits: int = 0
        self.misses: int = 0
        self.tokens_saved: int = 0

    def _normalize_key(self, query: str) -> str:
        """
        Normalizes query string by stripping accents, lowering, removing punctuation and trimming whitespace.
        """
        nfkd = unicodedata.normalize('NFKD', query)
        q = "".join([c for c in nfkd if not unicodedata.combining(c)]).lower().strip()
        q = re.sub(r'[^\w\s]', '', q)
        q = re.sub(r'\s+', ' ', q)
        return q

    def get(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves cached response if valid and not expired.
        """
        if not self.enabled:
            return None

        key = self._normalize_key(query)
        entry = self._cache.get(key)

        if not entry:
            self.misses += 1
            return None

        # Check expiration
        now = time.time()
        if now - entry["timestamp"] > self.ttl:
            del self._cache[key]
            self.misses += 1
            return None

        entry["hit_count"] += 1
        entry["last_accessed"] = now
        self.hits += 1
        self.tokens_saved += entry["data"].get("token_usage", {}).get("total_tokens", 0)

        return entry["data"]

    def set(self, query: str, data: Dict[str, Any]):
        """
        Stores response in cache.
        """
        if not self.enabled:
            return

        key = self._normalize_key(query)

        # Evict oldest entry if max_size reached
        if len(self._cache) >= self.max_size and key not in self._cache:
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k]["last_accessed"])
            del self._cache[oldest_key]

        now = time.time()
        self._cache[key] = {
            "timestamp": now,
            "last_accessed": now,
            "hit_count": 0,
            "data": data
        }

    def clear(self):
        """Clears all cached entries."""
        self._cache.clear()
        self.hits = 0
        self.misses = 0
        self.tokens_saved = 0

    def get_stats(self) -> Dict[str, Any]:
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0.0
        return {
            "cache_size": len(self._cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate_pct": round(hit_rate, 2),
            "tokens_saved": self.tokens_saved,
            "enabled": self.enabled
        }


# Global singleton instance
response_cache = ResponseCacheService()
