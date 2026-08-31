from __future__ import annotations
import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator

BASE_DIR = Path(__file__).resolve().parent.parent
IS_SERVERLESS = bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))
DEFAULT_CHROMA_PERSIST = "/tmp/chroma_db" if IS_SERVERLESS else str(BASE_DIR / "data" / "chroma_db")


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
    CHROMA_PERSIST_DIR: str = DEFAULT_CHROMA_PERSIST
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
    ESCALATION_EMAIL: str = "edig0rgudevia@gmail.com"
    ESCALATION_WHATSAPP: str = "+57 313 730 1501"
    ESCALATION_PHONE_RAW: str = "3137301501"
    ESCALATION_HOURS: str = "Lunes a Viernes 8:00 AM - 6:00 PM (COT)"

    @field_validator("PORT")
    @classmethod
    def validate_port(cls, v: int) -> int:
        if not (1 <= v <= 65535):
            raise ValueError("PORT must be between 1 and 65535.")
        return v

    @field_validator("SIMILARITY_THRESHOLD")
    @classmethod
    def validate_similarity(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("SIMILARITY_THRESHOLD must be between 0.0 and 1.0.")
        return v

    @field_validator("LLM_TEMPERATURE")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        if not (0.0 <= v <= 2.0):
            raise ValueError("LLM_TEMPERATURE must be between 0.0 and 2.0.")
        return v

    @field_validator("CHUNK_OVERLAP")
    @classmethod
    def validate_overlap(cls, v: int, info) -> int:
        chunk_size = info.data.get("CHUNK_SIZE", 500)
        if v >= chunk_size:
            raise ValueError("CHUNK_OVERLAP must be strictly smaller than CHUNK_SIZE.")
        return v


settings = Settings()
