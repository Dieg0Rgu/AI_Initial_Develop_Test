from __future__ import annotations
import re
import unicodedata
from typing import List, Dict, Any, Tuple

try:
    from app.config import settings
    from app.rag.vector_store import ChromaVectorStore
except ImportError:
    from backend.app.config import settings
    from backend.app.rag.vector_store import ChromaVectorStore

STOP_WORDS = {
    "de", "la", "que", "el", "en", "y", "a", "los", "del", "se", "las", "por", "un", "para",
    "con", "no", "una", "su", "al", "lo", "como", "mas", "pero", "sus", "le", "ya", "o",
    "este", "si", "porque", "esta", "son", "entre", "esta", "cuando", "muy", "sin", "sobre",
    "tambien", "me", "hasta", "hay", "donde", "quien", "desde", "todo", "nos", "durante",
    "todos", "uno", "les", "ni", "contra", "otros", "ese", "eso", "ante", "ellos", "e",
    "esto", "mi", "antes", "algunos", "que", "unos", "yo", "otro", "otras", "otra", "el",
    "tanto", "esa", "estos", "mucho", "quienes", "nada", "muchos", "cual", "poco", "ella",
    "estar", "estas", "algunas", "algo", "nosotros", "hola", "buenas", "tardes", "dias",
    "noches", "porfa", "favor", "quisiera", "saber", "tienen", "cuales", "cuanto", "como"
}

def normalize_text(text: str) -> str:
    nfkd = unicodedata.normalize('NFKD', text)
    return "".join([c for c in nfkd if not unicodedata.combining(c)]).lower()

class RAGRetriever:
    def __init__(self, vector_store: ChromaVectorStore = None):
        self.vector_store = vector_store or ChromaVectorStore()

    def _calculate_keyword_overlap(self, query: str, document_text: str) -> float:
        norm_query = normalize_text(query)
        norm_doc = normalize_text(document_text)

        words = re.findall(r'\b\w{3,}\b', norm_query)
        keywords = [w for w in words if w not in STOP_WORDS]

        if not keywords:
            return 0.0

        matches = sum(1 for kw in keywords if kw in norm_doc)
        return matches / len(keywords)

    def retrieve(self, query: str, top_k: int = None) -> Tuple[List[Dict[str, Any]], bool, str]:
        """
        Retrieves top relevant chunks for a user query using hybrid semantic + keyword scoring.
        """
        k = top_k or settings.TOP_K_RESULTS
        results = self.vector_store.query(query, top_k=k)

        docs = results.get("documents", [[]])[0] if results.get("documents") else []
        metas = results.get("metadatas", [[]])[0] if results.get("metadatas") else []
        distances = results.get("distances", [[]])[0] if results.get("distances") else []

        if not docs:
            return [], False, ""

        retrieved_chunks = []
        best_composite_score = 0.0

        for text, meta, dist in zip(docs, metas, distances):
            d_val = float(dist) if dist is not None else 0.5
            vector_sim = max(0.0, min(1.0, 1.0 - d_val))
            keyword_sim = self._calculate_keyword_overlap(query, text)

            # Hybrid score
            composite = (vector_sim * 0.6) + (keyword_sim * 0.4)
            if composite > best_composite_score:
                best_composite_score = composite

            retrieved_chunks.append({
                "id": meta.get("chunk_id", "unknown") if meta else "unknown",
                "text": text,
                "source": meta.get("source", "Documento del negocio") if meta else "Documento",
                "title": meta.get("title", "Información Gastroteacher") if meta else "Info",
                "category": meta.get("category", "General") if meta else "General",
                "similarity_score": round(composite, 4),
                "vector_similarity": round(vector_sim, 4),
                "keyword_overlap": round(keyword_sim, 4),
                "distance": round(d_val, 4)
            })

        # Sort chunks by composite similarity
        retrieved_chunks.sort(key=lambda x: x["similarity_score"], reverse=True)

        # In-scope relevance criteria
        is_relevant = (best_composite_score >= 0.20) or any(
            c["vector_similarity"] >= 0.25 and c["keyword_overlap"] > 0.0 for c in retrieved_chunks
        )

        # Build formatted context block for LLM prompt
        formatted_context_parts = []
        for i, chunk in enumerate(retrieved_chunks, start=1):
            formatted_context_parts.append(
                f"[DOCUMENTO {i}: {chunk['source']} | Título: {chunk['title']}]\n{chunk['text']}\n"
            )
        formatted_context = "\n---\n".join(formatted_context_parts)

        return retrieved_chunks, is_relevant, formatted_context
