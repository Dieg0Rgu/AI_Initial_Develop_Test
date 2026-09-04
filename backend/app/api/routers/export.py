from __future__ import annotations
import os
import time
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

try:
    from app.config import settings
    from app.utils.pdf_generator import GastroteacherPDFGenerator
except ImportError:
    from backend.app.config import settings
    from backend.app.utils.pdf_generator import GastroteacherPDFGenerator

router = APIRouter(prefix="/api/export", tags=["PDF, MD & TXT Export"])

_pdf_generator = GastroteacherPDFGenerator()


class ChatExportRequest(BaseModel):
    session_id: Optional[str] = Field("web_session", description="ID de sesión")
    messages: List[Dict[str, Any]] = Field(..., description="Lista de mensajes de la conversación")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadatos de la sesión")


@router.post("/chat-pdf")
async def export_chat_pdf(request: ChatExportRequest):
    """
    Exports the current chat conversation to a styled PDF file and streams it for download.
    """
    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages provided to export.")

    temp_dir = tempfile.gettempdir()
    pdf_filename = f"gastroteacher_chat_{request.session_id}_{int(os.times().elapsed)}.pdf"
    pdf_path = os.path.join(temp_dir, pdf_filename)

    try:
        _pdf_generator.convert_conversation_to_pdf(
            messages=request.messages,
            session_id=request.session_id,
            output_pdf_path=pdf_path,
            metadata=request.metadata
        )

        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename=f"gastroteacher_chat_{request.session_id}.pdf",
            headers={"Content-Disposition": f"attachment; filename=gastroteacher_chat_{request.session_id}.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")


@router.post("/chat-md")
async def export_chat_md(request: ChatExportRequest):
    """
    Exports the current chat conversation to a structured Markdown (.md) document and streams it for download.
    """
    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages provided to export.")

    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# Gastroteacher Academy - Transcripción de Conversación",
        "> **Asistente Virtual Comercial Oficial** | *Academia de Idiomas y Gastronomía en Colombia*\n",
        f"- **Sesión ID**: `{request.session_id}`",
        f"- **Fecha de Exportación**: `{current_time}`",
        f"- **Total de Mensajes**: `{len(request.messages)}`\n",
        "---",
        "\n## 💬 Historial de Interacción\n"
    ]

    for i, msg in enumerate(request.messages, start=1):
        role = msg.get("role", "user")
        content = msg.get("content", "").strip()
        latency = msg.get("latency_ms", 0.0)
        is_esc = msg.get("is_escalated", False)
        sources = msg.get("sources", [])

        if role == "user":
            lines.append(f"### 👤 {i}. Usuario")
            lines.append(f"> {content}\n")
        else:
            badge = " 🚨 `[Escalado a Asesor Humano]`" if is_esc else " ✨ `[Respuesta Automática RAG]`"
            lines.append(f"### 🤖 {i}. Asistente Gastroteacher{badge}\n")
            lines.append(f"{content}\n")
            if sources:
                lines.append("**📚 Fuentes Consultadas:**")
                for s in sources:
                    s_title = s.get("title", "Documento")
                    lines.append(f"- *{s_title}*")
                lines.append("")
            if latency and latency > 0:
                lines.append(f"*⚡ Latencia: {latency:.1f}ms*\n")
        lines.append("---\n")

    lines.append("## 📞 Canales Oficiales de Soporte y Admisiones")
    lines.append(f"- **Correo de Asesoría**: [{settings.ESCALATION_EMAIL}](mailto:{settings.ESCALATION_EMAIL})")
    lines.append(f"- **WhatsApp / Línea Oficial**: [{settings.ESCALATION_WHATSAPP}](https://wa.me/{settings.ESCALATION_PHONE_RAW})")
    lines.append(f"- **Horario de Atención**: {settings.ESCALATION_HOURS}")
    lines.append(f"- **Sedes**: Bogotá D.C. & Medellín, Colombia\n")
    lines.append("- **Sedes**: Bogotá D.C. & Medellín, Colombia\n")

    md_content = "\n".join(lines)

    temp_dir = tempfile.gettempdir()
    md_filename = f"gastroteacher_chat_{request.session_id}_{int(os.times().elapsed)}.md"
    md_path = os.path.join(temp_dir, md_filename)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    return FileResponse(
        path=md_path,
        media_type="text/markdown; charset=utf-8",
        filename=f"gastroteacher_chat_{request.session_id}.md",
        headers={"Content-Disposition": f"attachment; filename=gastroteacher_chat_{request.session_id}.md"}
    )


@router.post("/chat-txt")
async def export_chat_txt(request: ChatExportRequest):
    """
    Exports the current chat conversation to a clean plaintext (.txt) transcript and streams it for download.
    """
    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages provided to export.")

    lines = [
        "================================================================================",
        " GASTROTEACHER ACADEMY - TRANSCRIPCIÓN OFICIAL DE CONVERSACIÓN",
        " Academia de Idiomas y Gastronomía en Colombia",
        "================================================================================",
        f" Sesión ID     : {request.session_id}",
        f" Fecha Export  : {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f" Total Mensajes: {len(request.messages)}",
        "================================================================================\n"
    ]

    for i, msg in enumerate(request.messages, start=1):
        role = "USUARIO" if msg.get("role") == "user" else "ASISTENTE GASTROTEACHER"
        content = msg.get("content", "").strip()
        latency = msg.get("latency_ms", 0.0)
        is_esc = msg.get("is_escalated", False)

        status_tag = " [Escalado a Asesor Humano]" if is_esc else ""
        lines.append(f"[{i}] {role}{status_tag}")
        lines.append("-" * 80)
        lines.append(content)
        if latency and latency > 0:
            lines.append(f"  (Latencia: {latency:.1f}ms)")
        lines.append("\n" + "." * 80 + "\n")

    lines.append("================================================================================")
    lines.append(" FIN DE LA TRANSCRIPCIÓN - GASTROTEACHER AI SUPPORT ASSISTANT")
    lines.append(f" Contacto Humano: {settings.ESCALATION_EMAIL} | WhatsApp: {settings.ESCALATION_WHATSAPP}")
    lines.append("================================================================================")

    txt_content = "\n".join(lines)

    temp_dir = tempfile.gettempdir()
    txt_filename = f"gastroteacher_chat_{request.session_id}_{int(os.times().elapsed)}.txt"
    txt_path = os.path.join(temp_dir, txt_filename)
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(txt_content)

    return FileResponse(
        path=txt_path,
        media_type="text/plain; charset=utf-8",
        filename=f"gastroteacher_chat_{request.session_id}.txt",
        headers={"Content-Disposition": f"attachment; filename=gastroteacher_chat_{request.session_id}.txt"}
    )


@router.get("/documents")
async def list_official_documents_pdf():
    """
    Lists all available official business documents in PDF and Markdown format.
    """
    docs_dir = Path(settings.DOCUMENTS_DIR)
    workspace_root = Path(settings.DOCUMENTS_DIR).parents[1]
    exports_dir = workspace_root / "exports" / "pdf" / "documents"
    os.makedirs(exports_dir, exist_ok=True)

    available_docs = []
    if docs_dir.exists():
        for md_file in sorted(docs_dir.glob("*.md")):
            pdf_name = f"{md_file.stem}.pdf"
            pdf_path = exports_dir / pdf_name

            # Generate PDF if not existing
            if not pdf_path.exists():
                _pdf_generator.convert_markdown_to_pdf(str(md_file), str(pdf_path))

            size_kb = round(os.path.getsize(pdf_path) / 1024, 1)
            clean_title = md_file.stem
            if clean_title.startswith(("01_", "02_", "03_")):
                clean_title = clean_title[3:]
            clean_title = clean_title.replace("_", " ").title()

            available_docs.append({
                "id": md_file.stem,
                "title": clean_title,
                "filename": pdf_name,
                "md_filename": md_file.name,
                "size_kb": size_kb,
                "download_url": f"/api/export/documents/{pdf_name}"
            })

    return {"status": "success", "documents": available_docs}


@router.get("/documents/{filename}")
async def download_official_document_file(filename: str):
    """
    Downloads a specific official business document (PDF or Markdown).
    """
    docs_dir = Path(settings.DOCUMENTS_DIR)
    workspace_root = Path(settings.DOCUMENTS_DIR).parents[1]
    exports_dir = workspace_root / "exports" / "pdf" / "documents"

    if filename.endswith(".pdf"):
        pdf_path = exports_dir / filename
        if not pdf_path.exists():
            md_name = filename.replace(".pdf", ".md")
            md_path = docs_dir / md_name
            if md_path.exists():
                _pdf_generator.convert_markdown_to_pdf(str(md_path), str(pdf_path))
            else:
                raise HTTPException(status_code=404, detail="Document PDF not found.")

        return FileResponse(
            path=str(pdf_path),
            media_type="application/pdf",
            filename=filename,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    elif filename.endswith(".md"):
        md_path = docs_dir / filename
        if not md_path.exists():
            raise HTTPException(status_code=404, detail="Document Markdown file not found.")

        return FileResponse(
            path=str(md_path),
            media_type="text/markdown; charset=utf-8",
            filename=filename,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    raise HTTPException(status_code=400, detail="Unsupported file format.")


# Backwards compatibility alias
download_official_document_pdf = download_official_document_file
