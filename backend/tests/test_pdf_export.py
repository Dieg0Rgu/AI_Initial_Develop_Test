import os
from fastapi.testclient import TestClient
from app.main import app
from app.utils.pdf_generator import GastroteacherPDFGenerator
from app.utils.sweet_alert_console import SweetAlert

client = TestClient(app)


def test_markdown_to_pdf_conversion(tmp_path):
    generator = GastroteacherPDFGenerator()
    test_md = tmp_path / "test_doc.md"
    test_md.write_text("""# Gastroteacher Academy - Test Document
## 1. Introduction
This is a test document with **bold text**, *italic text*, and a bullet list:
- Item 1
- Item 2

| Level | Hours |
|---|---|
| A1 | 96 |
| B1 | 96 |
""", encoding="utf-8")

    out_pdf = tmp_path / "test_doc.pdf"
    res = generator.convert_markdown_to_pdf(str(test_md), str(out_pdf))

    assert os.path.exists(res)
    assert os.path.getsize(res) > 1000


def test_conversation_to_pdf_conversion(tmp_path):
    generator = GastroteacherPDFGenerator()
    messages = [
        {"role": "user", "content": "¿Cuáles son los horarios?", "latency_ms": 0.0},
        {"role": "assistant", "content": "Contamos con horarios entre semana y fines de semana.", "latency_ms": 35.0, "sources": [{"title": "Horarios Oficiales"}], "token_usage": {"total_tokens": 150}}
    ]

    out_pdf = tmp_path / "test_chat.pdf"
    res = generator.convert_conversation_to_pdf(messages, "test_session_123", str(out_pdf))

    assert os.path.exists(res)
    assert os.path.getsize(res) > 1000


def test_sweet_alert_renders_without_errors():
    SweetAlert.info("Test Info", "Information body message")
    SweetAlert.success("Test Success", "Success body message", {"Key": "Value"})
    SweetAlert.warning("Test Warning", "Warning body message")
    SweetAlert.error("Test Error", "Error body message")
    SweetAlert.render_summary_table("Test Summary", ["Col1", "Col2"], [["Val1", "Val2"]])


def test_api_export_chat_pdf():
    payload = {
        "session_id": "test_web_session",
        "messages": [
            {"role": "user", "content": "¿Cuáles son los precios?"},
            {"role": "assistant", "content": "El nivel vale $1.450.000 COP de contado."}
        ]
    }
    response = client.post("/api/export/chat-pdf", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert len(response.content) > 1000


def test_api_export_chat_md():
    payload = {
        "session_id": "test_web_session_md",
        "messages": [
            {"role": "user", "content": "¿Cuáles son los precios del curso?"},
            {"role": "assistant", "content": "El nivel vale $1.450.000 COP.", "is_escalated": False, "sources": [{"title": "Tarifas Oficiales"}], "latency_ms": 25.0}
        ]
    }
    response = client.post("/api/export/chat-md", json=payload)
    assert response.status_code == 200
    assert "markdown" in response.headers["content-type"] or "text" in response.headers["content-type"]
    assert "Gastroteacher Academy" in response.text
    assert "Tarifas Oficiales" in response.text


def test_api_export_chat_txt():
    payload = {
        "session_id": "test_web_session_txt",
        "messages": [
            {"role": "user", "content": "¿Cuáles son los horarios?"},
            {"role": "assistant", "content": "Horarios disponibles entre semana y fines de semana.", "latency_ms": 30.0}
        ]
    }
    response = client.post("/api/export/chat-txt", json=payload)
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert "GASTROTEACHER ACADEMY" in response.text
    assert "Horarios disponibles" in response.text


def test_api_export_documents_list_and_download():
    # 1. List documents
    res_list = client.get("/api/export/documents")
    assert res_list.status_code == 200
    data = res_list.json()
    assert data["status"] == "success"
    assert len(data["documents"]) >= 3

    # 2. Download first document as PDF
    first_doc_pdf = data["documents"][0]["filename"]
    res_download_pdf = client.get(f"/api/export/documents/{first_doc_pdf}")
    assert res_download_pdf.status_code == 200
    assert res_download_pdf.headers["content-type"] == "application/pdf"
    assert len(res_download_pdf.content) > 1000

    # 3. Download first document as Markdown (MD)
    first_doc_md = data["documents"][0].get("md_filename", "01_courses_modalities_levels.md")
    res_download_md = client.get(f"/api/export/documents/{first_doc_md}")
    assert res_download_md.status_code == 200
    assert "markdown" in res_download_md.headers["content-type"] or "text" in res_download_md.headers["content-type"]
    assert len(res_download_md.content) > 100
