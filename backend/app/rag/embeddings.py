from __future__ import annotations
import math
import hashlib
import unicodedata
from typing import List, Dict, Any
import httpx
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings

try:
    from app.config import settings
except ImportError:
    from backend.app.config import settings

class SmartEmbeddingFunction(EmbeddingFunction[Documents]):
    """
    Embedding function that prioritizes Ollama embeddings,
    with an internal deterministic semantic fallback for offline/isolated execution and testing.
    """
    def __init__(self, ollama_url: str = None, model: str = None):
        self.ollama_url = ollama_url or settings.OLLAMA_BASE_URL
        self.model = model or settings.OLLAMA_EMBED_MODEL
        self.dim = 384  # standard embedding dimensionality

    @staticmethod
    def name() -> str:
        return "smart_embedding_function"

    def get_config(self) -> Dict[str, Any]:
        return {
            "ollama_url": self.ollama_url,
            "model": self.model
        }

    @classmethod
    def build_from_config(cls, config: Dict[str, Any]) -> SmartEmbeddingFunction:
        return cls(
            ollama_url=config.get("ollama_url"),
            model=config.get("model")
        )

    def _clean_text(self, text: str) -> str:
        nfkd = unicodedata.normalize('NFKD', text)
        return "".join([c for c in nfkd if not unicodedata.combining(c)]).lower().strip()

    def _fallback_embed(self, text: str) -> List[float]:
        """
        Deterministic, dense vector embedding generated using semantic token hashing
        and n-gram frequency distribution.
        """
        vector = [0.0] * self.dim
        cleaned = self._clean_text(text)
        words = cleaned.split()

        tokens = words + [cleaned[i:i+3] for i in range(len(cleaned)-2)]
        for token in tokens:
            h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dim
            sign = 1.0 if ((h >> 8) % 2 == 0) else -1.0
            weight = 1.0 + (1.0 / (len(token) + 1))
            vector[idx] += sign * weight

        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0:
            vector = [v / norm for v in vector]
        return vector

    def _embed_via_ollama(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        with httpx.Client(base_url=self.ollama_url, timeout=5.0) as client:
            for text in texts:
                try:
                    response = client.post("/api/embeddings", json={
                        "model": self.model,
                        "prompt": text
                    })
                    if response.status_code == 200:
                        data = response.json()
                        embeddings.append(data.get("embedding", self._fallback_embed(text)))
                    else:
                        embeddings.append(self._fallback_embed(text))
                except Exception:
                    embeddings.append(self._fallback_embed(text))
        return embeddings

    def __call__(self, input: Documents) -> Embeddings:
        ollama_available = False
        try:
            with httpx.Client(base_url=self.ollama_url, timeout=0.5) as client:
                res = client.get("/api/tags")
                if res.status_code == 200:
                    ollama_available = True
        except Exception:
            ollama_available = False

        if ollama_available:
            return self._embed_via_ollama(list(input))
        else:
            return [self._fallback_embed(text) for text in input]
