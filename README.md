# Gastroteacher AI Customer Support Assistant (RAG + FastAPI + Vue 3)

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI_0.115+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![ChromaDB](https://img.shields.io/badge/Vector_DB-ChromaDB_1.5+-FC521F?style=flat)](https://www.trychroma.com/)
[![Ollama](https://img.shields.io/badge/LLM-Ollama_(qwen2.5/llama3.1)-black?style=flat&logo=ollama&logoColor=white)](https://ollama.com/)
[![Vue 3](https://img.shields.io/badge/Frontend-Vue_3_TypeScript-4FC08D?style=flat&logo=vue.js&logoColor=white)](https://vuejs.org/)
[![Tailwind CSS 4](https://img.shields.io/badge/Styles-Tailwind_CSS_4-38B2AC?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Tests](https://img.shields.io/badge/QA_Tests-16_Passed-brightgreen?style=flat)]()

An intelligent customer support assistant built for **Gastroteacher Academy** (a Colombian bilingual language academy specializing in culinary and hospitality English). The assistant answers prospective and current student inquiries about **schedules, prices, levels, enrollments, certifications, and modalities** using Retrieval-Augmented Generation (RAG) strictly grounded in official business documents, featuring automated human escalation, frequent answer caching, real-time analytics, and a modern Glassmorphism frontend.

---

## 🏛️ System Architecture

```
                                  +----------------------------+
                                  |    Vue 3 + Tailwind UI     |
                                  |  (Glassmorphism / Ambient) |
                                  +--------------+-------------+
                                                 |
                                     POST /api/chat | /api/webhook
                                                 v
+-----------------------------------------------------------------------------------------+
|                                    FastAPI BACKEND                                      |
|                                                                                         |
|  +---------------------+        +--------------------+        +----------------------+  |
|  | Frequent Response   | <====> |  RAG Hybrid Engine | ====>  | Human Escalation     |  |
|  | Cache (TTL & Hits)  | [Hit]  | (Vector + Keywords)| [Out]  | Manager & Contact    |  |
|  +---------------------+        +----------+---------+        +----------------------+  |
|                                            |                                            |
|                                            v Top-K Chunks                               |
|                                 +--------------------+                                  |
|                                 | ChromaDB Store     |                                  |
|                                 | (Embeddings & Cos) |                                  |
|                                 +----------+---------+                                  |
|                                            |                                            |
|                                            v Grounded Context                           |
|                                 +--------------------+                                  |
|                                 | Ollama Local LLM   |                                  |
|                                 | (qwen2.5 / llama3) |                                  |
|                                 +----------+---------+                                  |
|                                            |                                            |
|                                            v JSON Response                              |
|                          Answer + Sources + Escalation + Metrics                        |
+-----------------------------------------------------------------------------------------+
```

---

## 📂 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routers/
│   │   │       ├── chat.py           # /api/chat & /api/webhook endpoints
│   │   │       ├── documents.py      # /api/documents/ingest & /status
│   │   │       ├── health.py         # /api/health check
│   │   │       └── metrics.py        # /api/metrics analytics & reset
│   │   ├── cache/
│   │   │   └── cache_service.py      # Normalized response cache & hit tracking
│   │   ├── data/
│   │   │   ├── chroma_db/            # Persistent ChromaDB vector storage
│   │   │   └── documents/            # 3+ Official business Markdown documents
│   │   │       ├── 01_courses_modalities_levels.md
│   │   │       ├── 02_pricing_schedules_promotions.md
│   │   │       └── 03_enrollments_certifications_policies.md
│   │   ├── llm/
│   │   │   ├── client.py             # Ollama async HTTP client & token estimator
│   │   │   └── prompts.py            # System persona, constraints & 3+ few-shots
│   │   ├── metrics/
│   │   │   └── metrics_tracker.py    # Query count, token costs, escalation rate
│   │   ├── rag/
│   │   │   ├── chunker.py            # Text chunking with overlap
│   │   │   ├── embeddings.py         # Smart embedding function (Ollama + fallback)
│   │   │   ├── loader.py             # Business document markdown loader
│   │   │   ├── retriever.py          # Hybrid semantic + keyword retrieval
│   │   │   └── vector_store.py       # ChromaDB collection management
│   │   ├── config.py                 # Pydantic BaseSettings environment config
│   │   └── main.py                   # FastAPI application entrypoint
│   ├── tests/
│   │   ├── test_cache.py             # Cache set, normalization & hit rate tests
│   │   ├── test_ingestion.py         # 3+ docs loading & chunking tests
│   │   ├── test_rag_escalation.py    # Out-of-scope escalation tests
│   │   ├── test_rag_retrieval.py     # Relevant chunks query tests
│   │   └── test_webhook_api.py       # API endpoints & webhook integration tests
│   ├── qa_check.py                   # Standalone QA verification runner script
│   ├── requirements.txt              # Python backend dependencies
│   └── .env.example                  # Backend environment template
│
├── frontend/
│   └── Rage_frontend/
│       ├── src/
│       │   ├── components/
│       │   │   ├── ChatMessage.vue   # Glassmorphic bubble with source drawers
│       │   │   ├── MetricsModal.vue  # Real-time analytics modal
│       │   │   ├── Navbar.vue        # Gastroteacher logo, status, theme toggle
│       │   │   └── QuickPrompts.vue  # 1-click FAQ chips
│       │   ├── services/
│       │   │   └── api.ts            # Typed API client for FastAPI
│       │   ├── types/
│       │   │   └── chat.ts           # TypeScript interfaces
│       │   ├── App.vue               # Main responsive layout & chat timeline
│       │   ├── main.ts               # Vue application mount
│       │   └── style.css             # Pure Tailwind 4 import
│       ├── package.json
│       └── vite.config.ts
│
├── .env.example                      # Root configuration template
└── README.md                         # Documentation in English
```

---

## ⚙️ Environment Variables

Copy `.env.example` to `.env` in both root and `backend/` directory:

```bash
cp .env.example backend/.env
```

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `HOST` | `0.0.0.0` | Backend bind host address |
| `PORT` | `8000` | Backend API port |
| `ENVIRONMENT` | `development` | Environment mode (`development` / `production`) |
| `CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Allowed frontend origins |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama daemon local URL |
| `OLLAMA_MODEL` | `qwen2.5:7b` | Ollama chat model (`qwen2.5:7b` or `llama3.1:8b`) |
| `OLLAMA_EMBED_MODEL`| `nomic-embed-text` | Ollama embedding model |
| `LLM_TEMPERATURE` | `0.2` | Temperature for factual precision |
| `MAX_TOKENS` | `1024` | Maximum tokens per response |
| `CHROMA_PERSIST_DIR`| `./data/chroma_db` | Path for ChromaDB persistence |
| `CHROMA_COLLECTION_NAME`| `gastroteacher_knowledge_base` | Chroma collection name |
| `CHUNK_SIZE` | `500` | Characters per document chunk |
| `CHUNK_OVERLAP` | `100` | Character overlap between adjacent chunks |
| `SIMILARITY_THRESHOLD` | `0.45` | Maximum distance threshold for relevance |
| `CACHE_ENABLED` | `true` | Enable frequent response caching |
| `CACHE_TTL_SECONDS` | `3600` | Cache time-to-live in seconds |
| `MAX_CACHE_SIZE` | `500` | Maximum cached query entries |
| `ESCALATION_EMAIL` | `soporte@gastroteacher.edu.co` | Support email for human handoff |
| `ESCALATION_WHATSAPP` | `+57 301 732 5327` | Support WhatsApp for human handoff |

---

## 🚀 Quickstart & Execution

### 1. Prerequisites
- Python 3.12+
- Node.js 20+ & npm
- (Optional) [Ollama](https://ollama.com/) with `qwen2.5:7b` (`ollama run qwen2.5:7b`)

### 2. Backend Setup & Run

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be available at:
- **API Root**: http://localhost:8000
- **Interactive Swagger Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

### 3. Frontend Setup & Run

```bash
# In a new terminal, navigate to the frontend directory
cd frontend/Rage_frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```

Frontend will open at: **http://localhost:5173**

---

## 🧪 QA Testing & Verification

The project includes both a **Pytest test suite** (16 automated unit and integration tests) and a **standalone QA report runner**:

### Run Pytest Suite
```bash
cd backend
./venv/bin/python3 -m pytest tests/ -v
```

### Run Standalone QA Check Script
```bash
cd backend
./venv/bin/python3 qa_check.py
```

**Expected QA Output**:
```
======================================================================
 🚀 GASTROTEACHER AI ASSISTANT - QA VERIFICATION SUITE
======================================================================
✅ PASS | 1. Business Knowledge Base Loading            (3 documents loaded)
✅ PASS | 2. ChromaDB Vector Store Ingestion            (35 chunks indexed)
✅ PASS | 3. RAG Retrieval [Horarios y Jornadas]        (Score: 0.4935)
✅ PASS | 3. RAG Retrieval [Precios e Inversión]        (Score: 0.5292)
✅ PASS | 3. RAG Retrieval [Certificaciones MCER]       (Score: 0.2509)
✅ PASS | 3. RAG Retrieval [Modalidades y Sedes]        (Score: 0.3993)
✅ PASS | 4. Out-of-Scope Human Escalation              (Flagged correctly as escalated)
✅ PASS | 5. Frequent Response Cache                    (Latency: 0.02 ms)
✅ PASS | 6. Webhook Input Channel                      (Session: telegram_telegram_bot_user_42)
✅ PASS | 7. Real-Time Metrics & Cost Tracker           (Queries: 4, Esc. Rate: 25.0%)

======================================================================
 🚀 QA RESULTS: 10/10 TESTS PASSED (Completed in 0.3s)
======================================================================
🎉 ALL QA CHECKS PASSED PERFECTLY! BACKEND IS READY FOR PRODUCTION / FRONTEND INTEGRATION.
```

---

## 📡 API Reference & Usage Examples

### 1. Chat Interaction (`POST /api/chat`)

**Request**:
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "¿Cuáles son los precios del curso de inglés gastronómico y aceptan pagos a cuotas?",
    "session_id": "web_user_123",
    "bypass_cache": false
  }'
```

**Response**:
```json
{
  "response": "¡Hola! Con gusto te comparto la información de precios y facilidades de pago en Gastroteacher:\n\n- **Gastronomy & Hospitality English**: $1.980.000 COP por el programa completo de 120 horas (o $720.000 COP por módulo individual de 40 horas).\n- **Financiación**: Financiación directa a 0% de interés mediante pagaré digital...\n\n¿Te gustaría realizar tu test de nivelación gratuito para iniciar?",
  "is_escalated": false,
  "cached": false,
  "sources": [
    {
      "id": "02_pricing_schedules_promotions.md_chunk_1",
      "source": "02_pricing_schedules_promotions.md",
      "title": "Gastroteacher Academy - Precios, Horarios, Financiación y Promociones",
      "category": "pricing_schedules_promotions",
      "similarity_score": 0.5292,
      "excerpt": "Programa Especializado Gastronomy & Hospitality English (120 horas)..."
    }
  ],
  "token_usage": {
    "prompt_tokens": 140,
    "completion_tokens": 85,
    "total_tokens": 225
  },
  "latency_ms": 12.4,
  "session_id": "web_user_123"
}
```

### 2. Webhook Ingestion (`POST /api/webhook`)

**Request**:
```bash
curl -X POST http://localhost:8000/api/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hola, ¿cuándo inician las próximas clases?",
    "sender_id": "telegram_user_9921",
    "channel": "telegram",
    "metadata": {"chat_type": "private"}
  }'
```

### 3. Analytics & Metrics (`GET /api/metrics`)

**Request**:
```bash
curl http://localhost:8000/api/metrics
```

**Response**:
```json
{
  "total_queries": 42,
  "escalated_queries": 4,
  "resolved_by_ai_queries": 38,
  "escalation_rate_pct": 9.52,
  "tokens": {
    "prompt_tokens": 5880,
    "completion_tokens": 3570,
    "total_tokens": 9450,
    "tokens_saved_by_cache": 3200
  },
  "costs": {
    "estimated_cost_usd": 0.01418,
    "estimated_cost_cop": 56.7,
    "savings_by_cache_usd": 0.0048,
    "savings_by_cache_cop": 19.2,
    "local_ollama_actual_cost": "$0.00 (Local Open-Source Execution)"
  },
  "performance": {
    "avg_latency_ms": 14.8,
    "cache": {
      "cache_size": 18,
      "max_size": 500,
      "hits": 14,
      "misses": 28,
      "hit_rate_pct": 33.33,
      "tokens_saved": 3200,
      "enabled": true
    },
    "uptime_seconds": 1840
  }
}
```

---

## 🔒 Prompt Engineering & Anti-Hallucination Guardrails

The system prompt strictly adheres to:
1. **Authorized Context Only**: Answers are synthesized exclusively from verified ChromaDB chunks.
2. **Escalation Trigger**: If a question falls out-of-scope (e.g. immigration visas, mechanical repairs, cryptocurrency, third-party courses) or is ambiguous, the assistant injects the `[ESCALATE_HUMAN]` flag and routes the user to official WhatsApp and email channels.
3. **Calibrated Temperature**: Default temperature is set to `0.2` for deterministic and factual accuracy.
4. **Few-Shot Examples**: 3+ canonical examples guide tone, formatting, and escalation boundaries.

---

## 🎨 Frontend Features & Design System
- **Gastroteacher Brand**: Chef hat + graduation cap branding with dual identity (Languages + Gastronomy).
- **Glassmorphism**: Translucent cards (`backdrop-blur-2xl`), ambient glow orbs, subtle borders.
- **Palette**: Earth accents (terracotta `#c85a32`, amber `#d97706`, olive `#5a6e48`) over warm stone/slate neutral backgrounds.
- **Dark/Light Mode**: 1-click theme switcher persisted across views.
- **RAG Traceability**: Collapsible sources drawer revealing exact business document excerpts and similarity match scores.
- **Performance Pill**: Real-time display of response latency, token count, and cache status.
