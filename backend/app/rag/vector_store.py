from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings as ChromaSettings

try:
    from app.config import settings
    from app.rag.embeddings import SmartEmbeddingFunction
except ImportError:
    from backend.app.config import settings
    from backend.app.rag.embeddings import SmartEmbeddingFunction


class ChromaVectorStore:
    def __init__(self, persist_dir: str = None, collection_name: str = None):
        self.persist_dir = persist_dir or settings.CHROMA_PERSIST_DIR
        self.collection_name = collection_name or settings.CHROMA_COLLECTION_NAME
        self.embedding_fn = SmartEmbeddingFunction()

        # Resilient client initialization across local, serverless (/tmp) and in-memory
        try:
            Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
            self.client = chromadb.PersistentClient(
                path=self.persist_dir,
                settings=ChromaSettings(anonymized_telemetry=False)
            )
        except Exception:
            try:
                self.persist_dir = "/tmp/chroma_db"
                Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
                self.client = chromadb.PersistentClient(
                    path=self.persist_dir,
                    settings=ChromaSettings(anonymized_telemetry=False)
                )
            except Exception:
                self.client = chromadb.EphemeralClient(
                    settings=ChromaSettings(anonymized_telemetry=False)
                )

    def _get_collection(self):
        return self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"}
        )

    def count(self) -> int:
        try:
            return self._get_collection().count()
        except Exception:
            return 0

    def add_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        """
        Adds or upserts chunked documents to ChromaDB collection.
        """
        if not chunks:
            return 0

        ids = [chunk["id"] for chunk in chunks]
        texts = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]

        cleaned_metadatas = []
        for meta in metadatas:
            cleaned = {}
            for k, v in meta.items():
                if isinstance(v, (str, int, float, bool)):
                    cleaned[k] = v
                else:
                    cleaned[k] = str(v)
            cleaned_metadatas.append(cleaned)

        collection = self._get_collection()
        collection.upsert(
            ids=ids,
            documents=texts,
            metadatas=cleaned_metadatas
        )
        return len(ids)

    def query(self, query_text: str, top_k: int = None) -> Dict[str, Any]:
        """
        Queries the vector store for top_k most similar chunks.
        """
        k = top_k or settings.TOP_K_RESULTS
        if self.count() == 0:
            return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

        collection = self._get_collection()
        return collection.query(
            query_texts=[query_text],
            n_results=min(k, self.count()),
            include=["documents", "metadatas", "distances"]
        )

    def reset_collection(self):
        """
        Clears and recreates the collection.
        """
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass
        return self._get_collection()
