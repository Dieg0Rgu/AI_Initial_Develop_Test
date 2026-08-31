from __future__ import annotations
import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # Ollama Local LLM & Embeddings Settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:7b"
    OLLAMA_EMBED_MODEL: str = "nomic-embed-text"
    LLM_TEMPERATURE: float = 0.2
    MAX_TOKENS: int = 1024

    # ChromaDB & RAG Settings
    CHROMA_PERSIST_DIR: str = str(BASE_DIR / "data" / "chroma_db")
    CHROMA_COLLECTION_NAME: str = "gastroteacher_knowledge_base"
    DOCUMENTS_DIR: str = str(BASE_DIR / "data" / "documents")
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 100
    SIMILARITY_THRESHOLD: float = 0.45  # Relevance threshold for cosine distance
    TOP_K_RESULTS: int = 3

    # Caching Settings
    CACHE_ENABLED: bool = True
    CACHE_TTL_SECONDS: int = 3600
    MAX_CACHE_SIZE: int = 500

    # Human Escalation Settings
    ESCALATION_EMAIL: str = "soporte@gastroteacher.edu.co"
    ESCALATION_WHATSAPP: str = "+57 301 732 5327"
    ESCALATION_HOURS: str = "Lunes a Viernes 8:00 AM - 6:00 PM (COT)"

settings = Settings()
