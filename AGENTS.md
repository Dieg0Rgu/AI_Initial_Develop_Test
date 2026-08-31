# AGENTS.md

## 1. Purpose of this File
This document is a compact, high‑signal instruction guide for OpenCode agents working on this **Gastroteacher AI Assistant** repository.  Every bullet reflects a fact that an agent might miss without explicit guidance.

## 2. Project Overview
- **Primary language**: *Python 3.12*.
- **Framework**: *FastAPI*.
- **Data store**: *ChromaDB* persisted under `backend/data/chroma_db`.
- **LLM**: Local *Ollama* (`qwen2.5:7b` by default).
- **Key endpoints**:
  - `POST /api/chat` – chat with RAG + caching.
  - `POST /api/webhook` – webhook integration.
  - `GET /api/health` – health & connectivity status.
  - `POST /api/documents/ingest` – force re‑ingest all Markdown docs.
  - `GET /api/metrics` – real‑time analytics.
  - `POST /api/export/chat-pdf` – export chat to PDF.
- **CI**: `qa_check.py` orchestrates lint, tests, BDD, mutation, and coverage.

## 3. Environment Setup
```bash
# 1. Create a Python venv in `backend`
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy env defaults
cp .env.example .env
# (adjust any values if required)
```

> ⚡ **Important**: The Ollama daemon must be running (`ollama serve`) before starting the backend.

## 4. Running the Application
```bash
# From the repository root
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

*The `--reload` flag is for development.  Remove it for production.*

## 5. Running Tests & QA
| Step | Command | Notes |
|------|---------|-------|
| Unit / Integration | `pytest -v` | Tests under ``backend/tests``.
| Coverage | `pytest -v --cov=app --cov-fail-under=85` | Ensure ≥ 85 % coverage.
| Lint | `flake8 app --count --statistics` | Reports critical code style issues.
| Full QA Pipeline | `./qa_check.py` | Executes lint → BDD → mutation → lint again. All steps must pass.

### Run individual tests
```bash
# Entire test module
pytest backend/tests/test_chat_api.py

# A single test function
pytest -k test_chat_endpoint_valid_query
```

## 6. Manual Procedures
- **Re‑ingest documents after changes**: `curl -X POST http://localhost:8000/api/documents/ingest`.
- **Clear caching**: `curl -X POST http://localhost:8000/api/metrics/reset`.
- **Export a chat to PDF**:
  ```bash
  curl -X POST http://localhost:8000/api/export/chat-pdf \
    -H "Content-Type: application/json" \
    -d '{"session_id":"demo", "messages":[{"role":"user","content":"...."}]}'
  ```
- **Health check**: `curl http://localhost:8000/api/health`.

## 7. OpenCode Agent Considerations
1. **Environment Variables** – Agents should reference the `backend/.env` file for configuration, not hard‑code values.
2. **Start‑up Trigger** – The FastAPI application performs a check during startup: if the vector store is empty, it will run `ingest_all_documents()` automatically.  Agents that need an already populated store may trigger the ingestion endpoint once the DB is empty.
3. **Test Clients** – For integration tests, use `fastapi.testclient.TestClient` from the `app.main` module; agents may run similar in‑memory tests to verify endpoint logic.
4. **Observability** – All logs are printed to stdout; agents can capture output using `subprocess` if needed.
5. **LLM Availability** – If Ollama is not reachable, `is_healthy()` returns ``False`` and the `/api/health` endpoint will report `connected: false`.  Agents should handle this gracefully.

## 8. Common Gotchas
- **ChromaDB Persistence** – Data is stored in `backend/data/chroma_db`.  Deleting that folder or modifying `CHROMA_PERSIST_DIR` will reset the vector store.
- **Cache TTL** – Controlled by the `CACHE_TTL_SECONDS` environment variable; default is `3600` seconds.
- **Locale** – The server defaults to `es` for responses unless the `language` field in the request payload is set to `en`.
- **Multi‑Language Support** – Switching `language` does not change LLM embeddings; only affects prompt text and response language.

---

> *This file is deliberately concise; it focuses on the concrete facts an agent needs to interact reliably with the project.*