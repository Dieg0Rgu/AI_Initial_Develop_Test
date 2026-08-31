from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    from app.config import settings
    from app.api.routers import chat, documents, metrics, health
    from app.api.routers.documents import ingest_all_documents
    from app.rag.vector_store import ChromaVectorStore
except ImportError:
    from backend.app.config import settings
    from backend.app.api.routers import chat, documents, metrics, health
    from backend.app.api.routers.documents import ingest_all_documents
    from backend.app.rag.vector_store import ChromaVectorStore

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure vector store has documents indexed
    vs = ChromaVectorStore()
    if vs.count() == 0:
        print("[Startup] Vector database is empty. Ingesting business documents...")
        ingest_all_documents()
        print(f"[Startup] Ingestion completed. Total chunks in ChromaDB: {vs.count()}")
    else:
        print(f"[Startup] Vector database ready with {vs.count()} chunks.")
    yield
    print("[Shutdown] Cleaning up resources...")

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
)

# Register routers
app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(metrics.router)
app.include_router(health.router)

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
