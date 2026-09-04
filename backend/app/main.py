from __future__ import annotations
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

try:
    from app.config import settings
    from app.exceptions import GastroteacherException
    from app.utils.logger import logger
    from app.api.routers import chat, documents, metrics, health, export, nonsense, auth
    from app.api.routers.documents import ingest_all_documents
    from app.rag.vector_store import ChromaVectorStore
except ImportError:
    from backend.app.config import settings
    from backend.app.exceptions import GastroteacherException
    from backend.app.utils.logger import logger
    from backend.app.api.routers import chat, documents, metrics, health, export, nonsense, auth
    from backend.app.api.routers.documents import ingest_all_documents
    from backend.app.rag.vector_store import ChromaVectorStore


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure vector store has documents indexed
    logger.info("Initializing Gastroteacher Assistant Backend...")
    try:
        vs = ChromaVectorStore()
        if vs.count() == 0:
            logger.info("Vector database is empty. Automatically ingesting official business documents...")
            ingest_all_documents()
            logger.info(f"Ingestion completed. Total chunks in ChromaDB: {vs.count()}")
        else:
            logger.info(f"Vector database ready with {vs.count()} chunks.")
    except Exception as e:
        logger.warning(f"[WARNING] Startup initialization skipped in serverless environment: {e}")

    yield

    logger.info("Shutting down Gastroteacher Assistant Backend...")


app = FastAPI(
    title="Gastroteacher AI Customer Support Assistant API",
    description="RAG-powered intelligent customer support assistant for Gastroteacher Colombian Language Academy.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for Vue 3 frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
    logger.info(f"{request.method} {request.url.path} - Status: {response.status_code} ({duration_ms}ms)")
    return response


# Global Exception Handlers
@app.exception_handler(GastroteacherException)
async def domain_exception_handler(request: Request, exc: GastroteacherException):
    logger.warning(f"Domain exception on {request.url.path}: {exc.message} (Status {exc.status_code})")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "error_type": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details
        }
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error_type": "InternalServerError",
            "message": "An unexpected server error occurred. Please contact technical support.",
            "details": {"path": str(request.url.path)}
        }
    )


# Register routers
app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(metrics.router)
app.include_router(health.router)
app.include_router(export.router)
app.include_router(nonsense.router)
app.include_router(auth.router)


@app.get("/")
async def root():
    return {
        "service": "Gastroteacher AI Assistant Backend",
        "status": "operational",
        "docs_url": "/docs",
        "health_url": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
