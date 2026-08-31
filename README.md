# Gastroteacher AI Customer Support Assistant (RAG + FastAPI + Vue 3)

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI_0.115+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![ChromaDB](https://img.shields.io/badge/Vector_DB-ChromaDB_1.5+-FC521F?style=flat)](https://www.trychroma.com/)
[![Ollama](https://img.shields.io/badge/LLM-Ollama_(qwen2.5/llama3.1)-black?style=flat&logo=ollama&logoColor=white)](https://ollama.com/)
[![Vue 3](https://img.shields.io/badge/Frontend-Vue_3_TypeScript-4FC08D?style=flat&logo=vue.js&logoColor=white)](https://vuejs.org/)
[![Tailwind CSS 4](https://img.shields.io/badge/Styles-Tailwind_CSS_4-38B2AC?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![SweetAlert2](https://img.shields.io/badge/UI_Alerts-SweetAlert2-orange?style=flat)](https://sweetalert2.github.io/)
[![Anime.js](https://img.shields.io/badge/Animations-Anime.js_4-purple?style=flat)](https://animejs.com/)
[![Moment.js](https://img.shields.io/badge/Localization-Moment.js-blue?style=flat)](https://momentjs.com/)
[![Tests](https://img.shields.io/badge/QA_Tests-77_Passed_(87.4%25_Coverage)-brightgreen?style=flat)]()
[![QA Pipeline](https://img.shields.io/badge/QA_Pipeline-PyTest_|_BDD_|_Mutation_|_Flake8-blueviolet?style=flat)]()

An enterprise-grade, intelligent customer support assistant built for **Gastroteacher Academy** (a premier Colombian bilingual language academy specializing in culinary and hospitality English). The assistant resolves prospective and current student inquiries about **schedules, prices, CEFR levels, enrollments, certifications, city transfers, and modalities** using Retrieval-Augmented Generation (RAG) strictly grounded in official business documents.

Key capabilities include **strict intent classification (Grupo A: Mandatory Escalation vs. Grupo B: Valid In-Scope Queries)**, multi-format conversation export (**PDF, Markdown, TXT**), automated human handoff, high-performance in-memory caching, structured JSON logging, dynamic UI animations (**Anime.js**), localized time formatting (**Moment.js**), interactive modals (**SweetAlert2**), and a modern Glassmorphic Vue 3 interface.

---

## 🏛️ System Architecture

```
                                  +----------------------------+
                                  |    Vue 3 + Tailwind UI     |
                                  |  (SweetAlert2 / Anime.js)  |
                                  +--------------+-------------+
                                                 |
                                     POST /api/chat | /api/export/*
                                                 v
+-----------------------------------------------------------------------------------------+
|                                    FastAPI BACKEND                                      |
|                                                                                         |
|  +---------------------+        +--------------------+        +----------------------+  |
|  | Frequent Response   | <====> |  RAG Hybrid Engine | ====>  | Human Escalation     |  |
|  | Cache (TTL & Hits)  | [Hit]  | (Vector + Keywords)| [Out]  | Manager (Grupo A)    |  |
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
|                                                                                         |
|  +-----------------------------------------------------------------------------------+  |
|  | Export Engine: PDF (ReportLab) | Markdown (.md) | Plain Text (.txt)               |  |
|  +-----------------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------------+
```

---

## 🎨 Frontend UI Libraries & Animations

The frontend client integrates top-tier open-source UI libraries for high interactivity and seamless user experience:

1. **SweetAlert2 (`sweetalert2`)**:
   - **Export & Download Toasts**: Non-intrusive notification toasts when downloading chat transcripts (PDF, Markdown, TXT) and official documents.
   - **Interactive Confirmation Dialogs**: Themed modal alerts for server metrics reset confirmation and clearing conversation history.
   - **Dark & Light Mode Harmony**: Automatically adapts background (`#1c1917` / `#ffffff`) and accent colors based on the current theme.

2. **Anime.js (`animejs`)**:
   - **Message Bubble Entrance**: Smooth physics-based translation and fade-in animations on every new incoming user or assistant message.
   - **Escalation Alert Transitions**: Elastic slide-in (`outElastic`) and exit transitions for the real-time human escalation banner.
   - **Modal Backdrop Effects**: Gentle zoom and blur entrance animations.

3. **Moment.js (`moment`)**:
   - **Localized Timestamps**: Full bilingual support (`es` / `en`) with custom formatting (`moment().format('LT')`).
   - **Detailed Escalation Logs**: Exact human handoff timestamps (`D de MMMM de YYYY, h:mm:ss a`).

---

## 📂 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routers/
│   │   │       ├── chat.py           # /api/chat & /api/webhook endpoints
│   │   │       ├── documents.py      # /api/documents/ingest & /status
│   │   │       ├── export.py         # Multi-format exports: PDF, Markdown & TXT
│   │   │       ├── health.py         # /api/health check
│   │   │       └── metrics.py        # /api/metrics analytics & reset
│   │   ├── cache/
│   │   │   └── cache_service.py      # Normalized response cache & hit tracking
│   │   ├── data/
│   │   │   ├── chroma_db/            # Persistent ChromaDB vector storage
│   │   │   └── documents/            # 3 Official business Markdown documents
│   │   │       ├── 01_courses_modalities_levels.md
│   │   │       ├── 02_pricing_schedules_promotions.md
│   │   │       └── 03_enrollments_certifications_policies.md
│   │   ├── exceptions.py             # Custom exception hierarchy & HTTP status mapping
│   │   ├── llm/
│   │   │   ├── client.py             # Ollama async client, intent router & fallback
│   │   │   └── prompts.py            # Strict Grupo A / Grupo B prompt & few-shots
│   │   ├── metrics/
│   │   │   └── metrics_tracker.py    # Query count, token costs, escalation rate
│   │   ├── rag/
│   │   │   ├── chunker.py            # Text chunking with overlap & metadata
│   │   │   ├── embeddings.py         # Smart embedding function (Ollama + fallback)
│   │   │   ├── loader.py             # Business document markdown loader
│   │   │   ├── retriever.py          # Hybrid semantic + keyword retrieval
│   │   │   └── vector_store.py       # ChromaDB collection management
│   │   ├── utils/
│   │   │   ├── logger.py             # Structured JSON logging & latency tracking
│   │   │   ├── pdf_generator.py      # ReportLab PDF generator for chats & docs
│   │   │   └── sweet_alert_console.py# Rich console banners for CI/CD reports
│   │   ├── config.py                 # Pydantic BaseSettings environment config & validators
│   │   └── main.py                   # FastAPI app entrypoint, middleware & exception handlers
│   ├── features/                     # BDD / Gherkin feature files (Behave)
│   │   └── escalation_and_cache.feature
│   ├── tests/
│   │   ├── conftest.py               # Shared PyTest fixtures
│   │   ├── test_cache.py             # Cache operations & normalization
│   │   ├── test_command_router.py    # API endpoints routing verification
│   │   ├── test_config_and_logging.py# Settings validation & structured logs
│   │   ├── test_core_logic.py        # Tokenizer, NLP & hybrid similarity scoring
│   │   ├── test_coverage_boost.py    # Edge cases & comprehensive coverage
│   │   ├── test_error_handling.py    # Graceful degradation & outage resilience
│   │   ├── test_ingestion.py         # 3 docs loading & chunking tests
│   │   ├── test_mocked_llm.py        # Ollama unit tests with mock fixtures
│   │   ├── test_pdf_export.py        # PDF, Markdown & TXT export tests
│   │   ├── test_rag_escalation.py    # Intent classification & realistic handoff tests
│   │   ├── test_rag_retrieval.py     # Relevant chunks query tests
│   │   └── test_webhook_api.py       # Webhook ingestion & health checks
│   ├── qa_check.py                   # Master QA orchestrator (PyTest + BDD + Mutation + Flake8)
│   ├── requirements.txt              # Python backend dependencies
│   └── .env.example                  # Backend environment template
│
├── frontend/
│   └── Rage_frontend/
│       ├── src/
│       │   ├── components/
│       │   │   ├── ChatMessage.vue   # Message bubble with Anime.js & Moment.js
│       │   │   ├── EscalationToast.vue# Elastic toast with SweetAlert2 and Anime.js
│       │   │   ├── ExportPdfModal.vue# Multi-format export with SweetAlert2 toasts
│       │   │   ├── MetricsModal.vue  # Real-time analytics with SweetAlert2 confirm
│       │   │   ├── Navbar.vue        # Gastroteacher logo, status & theme toggle
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
| `PORT` | `8000` | Backend API port (validated 1024-65535) |
| `ENVIRONMENT` | `development` | Environment mode (`development` / `production`) |
| `CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Allowed frontend origins |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama daemon local URL |
| `OLLAMA_MODEL` | `qwen2.5:7b` | Ollama chat model (`qwen2.5:7b` or `llama3.1:8b`) |
| `OLLAMA_EMBED_MODEL`| `nomic-embed-text` | Ollama embedding model |
| `LLM_TEMPERATURE` | `0.2` | Temperature for factual precision (0.0-1.0) |
| `MAX_TOKENS` | `1024` | Maximum tokens per response |
| `CHROMA_PERSIST_DIR`| `./data/chroma_db` | Path for ChromaDB persistence |
| `CHROMA_COLLECTION_NAME`| `gastroteacher_knowledge_base` | Chroma collection name |
| `CHUNK_SIZE` | `500` | Characters per document chunk |
| `CHUNK_OVERLAP` | `100` | Character overlap between adjacent chunks |
| `SIMILARITY_THRESHOLD` | `0.45` | Maximum distance threshold for relevance |
| `CACHE_ENABLED` | `true` | Enable frequent response caching |
| `CACHE_TTL_SECONDS` | `3600` | Cache time-to-live in seconds |
| `MAX_CACHE_SIZE` | `500` | Maximum cached query entries |
| `ESCALATION_EMAIL` | `edig0rgudevia@gmail.com` | Official email for human handoff |
| `ESCALATION_WHATSAPP` | `+57 313 730 1501` | Official WhatsApp line for human handoff |
| `ESCALATION_PHONE_RAW` | `573137301501` | Raw phone number for `wa.me` links |
| `ESCALATION_HOURS` | `Lunes a Viernes 8:00 AM - 6:00 PM (COT)` | Business hours for customer support |

---

## 🚀 Quickstart & Execution

### 1. Prerequisites
- Python 3.12+
- Node.js 20+ & npm
- [Ollama](https://ollama.com/) with `qwen2.5:7b` (`ollama serve` and `ollama run qwen2.5:7b`)

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

Backend endpoints:
- **API Root**: http://localhost:8000
- **Interactive Swagger Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

### 3. Frontend Setup & Run

```bash
# In a new terminal, navigate to the frontend directory
cd frontend/Rage_frontend

# Install dependencies (including sweetalert2, animejs, moment)
npm install

# Start Vite development server
npm run dev
```

Frontend will open at: **http://localhost:5173**

---

## 🛡️ Intent Classification & Escalation Engine

The assistant implements a strict two-tier classification system:

### GRUPO A: Immediate Human Escalation (`is_escalated = True`)
Triggers the `[ESCALATE_HUMAN]` protocol with tailored empathy and official contact channels for:
1. **Refunds & Payment Disputes**: Requests for refunds, chargebacks, or bank account returns due to job transfers or cancellations.
2. **Technical Support**: Virtual campus login failures, 403 Forbidden errors, missing recording access, or PSE payment processing issues.
3. **Corporate Agreements**: B2B bulk enrollment proposals (e.g. 50 chefs), 60-day invoices, and custom business pricing.
4. **Visa & Immigration**: Consular visa applications, overseas employment sponsorship, and cruise placement inquiries.
5. **Out-of-Scope Topics**: Practical cooking recipes, wine pairings, mechanics, cryptocurrency, or prompt injection/jailbreak attempts.
6. **Direct Human Request**: Explicit request to talk to a human advisor.

### GRUPO B: Valid In-Scope Academic & Commercial Queries
Handled automatically using verified ChromaDB RAG context:
- **Courses & Levels**: General English (A1-C1) and Gastronomy & Hospitality English (120 hrs).
- **Pricing & Payment**: $1,450,000 COP/level (General) or $1,980,000 COP (Gastronomy), with 0% interest direct financing.
- **Schedules & Modalities**: Morning, afternoon, and evening shifts; intensive Saturdays and Sunday mornings; in-person (Bogotá & Medellín) and 100% live online.
- **City Transfers & Relocation**: Free campus transfer between Bogotá and Medellín, instant switch to online live mode, or enrollment freezing for up to 90 days.

---

## 🧪 QA Testing & Quality Pipeline

The project features a **100% automated Quality Assurance Pipeline** orchestrated by `qa_check.py`:

```bash
# From repository root
./backend/venv/bin/python backend/qa_check.py
```

### Evaluation Phases & Thresholds:
1. **PyTest Unit & Integration Suite**: 77 automated tests validating API routing, RAG retrieval, Ollama client, cache normalization, structured logging, PDF/MD exports, and custom exceptions.
2. **Code Coverage**: Requires ≥ 85% total code coverage (currently at **87.41%**).
3. **BDD / Gherkin Cucumber Suite (Behave)**: Validates human escalation and cache retrieval behavioral specifications.
4. **Mutation Testing (Threshold Resilience)**: Assesses retriever robustness against mutation operators (score ≥ 0.20).
5. **Static Code Analysis (Flake8)**: Enforces PEP 8 syntax standards and zero undefined variables.

```
================================================================================
 🚀 INICIANDO ORQUESTADOR DE PRUEBAS DE CALIDAD - GASTROTEACHER QA ECOSYSTEM
================================================================================
▶️  PyTest Unit & Integration Suite:    ✅ APROBADO (77 pruebas, 87.41% cobertura)
▶️  BDD / Gherkin Behave Suite:         ✅ APROBADO (Escenarios de escalamiento y caché)
▶️  Mutation Testing Resilience:        ✅ APROBADO (Score >= 0.20)
▶️  Static Code Analysis (Flake8):       ✅ APROBADO (0 errores críticos)
================================================================================
 🎉 ¡Ecosistema de Calidad 100% Validado! READY FOR PRODUCTION
================================================================================
```

---

## 📡 API Reference & Endpoints

### 1. Chat Processing (`POST /api/chat`)
Processes queries through RAG, cache check, and intent classification.

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "¿Cuáles son los precios del curso y los métodos de pago?",
    "session_id": "web_session_1",
    "bypass_cache": false,
    "language": "es"
  }'
```

### 2. Multi-Format Chat Export
- **PDF Export**: `POST /api/export/chat-pdf` (ReportLab editorial styling)
- **Markdown Export**: `POST /api/export/chat-md` (Structured markdown with badges & sources)
- **Plain Text Export**: `POST /api/export/chat-txt` (Clean monospace transcript)

```bash
curl -X POST http://localhost:8000/api/export/chat-md \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "demo_export",
    "messages": [
      {"role": "user", "content": "¿Tienen clases los sábados?"},
      {"role": "assistant", "content": "Sí, contamos con jornada intensiva de 8:00 AM a 1:00 PM."}
    ]
  }' --output chat_transcript.md
```

### 3. Official Documents Catalog & Download
- **List Documents**: `GET /api/export/documents`
- **Download Document**: `GET /api/export/documents/{filename}` (supports `.pdf` and `.md`)

### 4. Real-Time Analytics (`GET /api/metrics`)
Returns total query counts, escalation rates, token consumption, and cache savings.

---

## 👥 Support & Official Contact
- **Admissions & Support Email**: `edig0rgudevia@gmail.com`
- **WhatsApp / Telegram Line**: `+57 313 730 1501`
- **Business Hours**: Lunes a Viernes 8:00 AM - 6:00 PM (COT)
- **Physical Campuses**: Bogotá D.C. (Chapinero) & Medellín (El Poblado), Colombia.
