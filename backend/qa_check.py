#!/usr/bin/env python3
"""
Gastroteacher AI Assistant - Comprehensive QA Verification Runner
Executes full regression, RAG retrieval, threshold escalation, caching, and API tests.
"""
import sys
import time
from pathlib import Path

# Add backend to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.rag.loader import DocumentLoader
from app.rag.chunker import TextChunker
from app.rag.vector_store import ChromaVectorStore
from app.rag.retriever import RAGRetriever
from app.cache.cache_service import response_cache
from app.metrics.metrics_tracker import metrics_tracker
from app.api.routers.documents import ingest_all_documents
from fastapi.testclient import TestClient
from app.main import app

def print_header(title: str):
    print("\n" + "=" * 70)
    print(f" 🚀 {title}")
    print("=" * 70)

def print_test(name: str, passed: bool, details: str = ""):
    icon = "✅ PASS" if passed else "❌ FAIL"
    print(f"{icon} | {name:<45} {details}")

def run_qa():
    print_header("GASTROTEACHER AI ASSISTANT - QA VERIFICATION SUITE")
    start_all = time.time()
    passed_tests = 0
    total_tests = 0

    # 1. Document Loading Check
    total_tests += 1
    loader = DocumentLoader()
    docs = loader.load_documents()
    if len(docs) >= 3:
        passed_tests += 1
        print_test("1. Business Knowledge Base Loading", True, f"({len(docs)} documents loaded)")
    else:
        print_test("1. Business Knowledge Base Loading", False, f"({len(docs)} documents found, expected >= 3)")

    # 2. Ingestion & Vector Storage
    total_tests += 1
    ingest_res = ingest_all_documents()
    vs = ChromaVectorStore()
    count = vs.count()
    if ingest_res["status"] == "success" and count > 0:
        passed_tests += 1
        print_test("2. ChromaDB Vector Store Ingestion", True, f"({count} chunks indexed)")
    else:
        print_test("2. ChromaDB Vector Store Ingestion", False, f"({count} chunks)")

    # 3. RAG Retrieval Precision Tests
    retriever = RAGRetriever(vs)
    queries = [
        ("Horarios y Jornadas", "¿Cuáles son los horarios de clases los sábados y noches?", ["02_pricing_schedules_promotions.md", "01_courses_modalities_levels.md"]),
        ("Precios e Inversión", "¿Cuánto cuesta el programa de Gastronomy English?", ["02_pricing_schedules_promotions.md"]),
        ("Certificaciones MCER", "¿Qué certificación entregan y preparan para TOEFL o IELTS?", ["03_enrollments_certifications_policies.md"]),
        ("Modalidades y Sedes", "¿Tienen clases presenciales en Bogotá y Medellín?", ["01_courses_modalities_levels.md"])
    ]

    for label, query, expected_sources in queries:
        total_tests += 1
        chunks, is_relevant, ctx = retriever.retrieve(query)
        has_source = any(any(src in c["source"] for src in expected_sources) for c in chunks)
        if is_relevant and has_source:
            passed_tests += 1
            print_test(f"3. RAG Retrieval [{label}]", True, f"(Score: {chunks[0]['similarity_score']})")
        else:
            print_test(f"3. RAG Retrieval [{label}]", False, f"(Relevant: {is_relevant})")

    # 4. Out-of-Scope Human Escalation
    total_tests += 1
    out_query = "¿Cómo reparar el carburador de una motocicleta Yamaha?"
    client = TestClient(app)
    res_esc = client.post("/api/chat", json={"message": out_query, "bypass_cache": True})
    esc_data = res_esc.json()
    if res_esc.status_code == 200 and esc_data["is_escalated"]:
        passed_tests += 1
        print_test("4. Out-of-Scope Human Escalation", True, "(Flagged correctly as escalated)")
    else:
        print_test("4. Out-of-Scope Human Escalation", False, f"(Status: {res_esc.status_code}, Escalated: {esc_data.get('is_escalated')})")

    # 5. Frequent Response Cache
    total_tests += 1
    cache_query = "¿Cuáles son los precios de los cursos de inglés?"
    client.post("/api/chat", json={"message": cache_query, "bypass_cache": False})
    res_cached = client.post("/api/chat", json={"message": cache_query, "bypass_cache": False})
    cache_json = res_cached.json()
    if cache_json.get("cached") is True:
        passed_tests += 1
        print_test("5. Frequent Response Cache", True, f"(Latency: {cache_json.get('latency_ms')} ms)")
    else:
        print_test("5. Frequent Response Cache", False, "(Response was not served from cache)")

    # 6. Webhook Integration Channel
    total_tests += 1
    res_webhook = client.post("/api/webhook", json={
        "message": "Hola, ¿cómo me inscribo?",
        "sender_id": "telegram_bot_user_42",
        "channel": "telegram"
    })
    webhook_json = res_webhook.json()
    if res_webhook.status_code == 200 and "response" in webhook_json:
        passed_tests += 1
        print_test("6. Webhook Input Channel", True, f"(Session: {webhook_json.get('session_id')})")
    else:
        print_test("6. Webhook Input Channel", False, f"(Status: {res_webhook.status_code})")

    # 7. Metrics & Token Analytics
    total_tests += 1
    res_metrics = client.get("/api/metrics")
    metrics_data = res_metrics.json()
    if res_metrics.status_code == 200 and metrics_data["total_queries"] > 0:
        passed_tests += 1
        print_test("7. Real-Time Metrics & Cost Tracker", True, f"(Queries: {metrics_data['total_queries']}, Esc. Rate: {metrics_data['escalation_rate_pct']}%)")
    else:
        print_test("7. Real-Time Metrics & Cost Tracker", False, f"(Status: {res_metrics.status_code})")

    duration = round(time.time() - start_all, 2)
    print_header(f"QA RESULTS: {passed_tests}/{total_tests} TESTS PASSED (Completed in {duration}s)")

    if passed_tests == total_tests:
        print("\n🎉 ALL QA CHECKS PASSED PERFECTLY! BACKEND IS READY FOR PRODUCTION / FRONTEND INTEGRATION.\n")
        return 0
    else:
        print(f"\n⚠️ {total_tests - passed_tests} TEST(S) FAILED. Please inspect the output above.\n")
        return 1

if __name__ == "__main__":
    sys.exit(run_qa())
