from __future__ import annotations
from typing import Optional, Dict, Any


class GastroteacherException(Exception):
    """Base exception for all domain-specific errors in Gastroteacher Assistant."""

    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class OllamaServiceUnavailableError(GastroteacherException):
    """Raised when the Ollama LLM service cannot be reached or times out."""

    def __init__(self, message: str = "Ollama LLM service is unavailable or timed out.", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=503, details=details)


class VectorStoreUnavailableError(GastroteacherException):
    """Raised when ChromaDB vector store encounters an unrecoverable error."""

    def __init__(self, message: str = "ChromaDB vector store is unavailable.", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=503, details=details)


class RAGRetrievalError(GastroteacherException):
    """Raised when an error occurs during similarity search or context retrieval."""

    def __init__(self, message: str = "Failed to retrieve relevant context chunks.", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=500, details=details)


class DocumentIngestionError(GastroteacherException):
    """Raised when parsing or indexing business documents fails."""

    def __init__(self, message: str = "Failed to load and index documents into vector store.", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=500, details=details)


class PDFExportException(GastroteacherException):
    """Raised when converting markdown or chat sessions to PDF fails."""

    def __init__(self, message: str = "Failed to compile document to PDF.", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=500, details=details)


class InvalidQueryException(GastroteacherException):
    """Raised when user input query is malformed or exceeds limits."""

    def __init__(self, message: str = "Invalid query payload provided.", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=400, details=details)
