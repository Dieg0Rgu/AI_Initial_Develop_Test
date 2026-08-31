from __future__ import annotations
import os
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

router = APIRouter(prefix="/api/export", tags=["PDF Export"])

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

    # Create temporary PDF file
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

@router.get("/documents")
async def list_official_documents_pdf():
    """
    Lists all available official business documents in PDF format.
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

            # Generate if not existing
            if not pdf_path.exists():
                _pdf_generator.convert_markdown_to_pdf(str(md_file), str(pdf_path))

            size_kb = round(os.path.getsize(pdf_path) / 1024, 1)
            # Friendly human readable title
            clean_title = md_file.stem
            if clean_title.startswith(("01_", "02_", "03_")):
                clean_title = clean_title[3:]
            clean_title = clean_title.replace("_", " ").title()

            available_docs.append({
                "id": md_file.stem,
                "title": clean_title,
                "filename": pdf_name,
                "size_kb": size_kb,
                "download_url": f"/api/export/documents/{pdf_name}"
            })

    return {"status": "success", "documents": available_docs}

@router.get("/documents/{pdf_filename}")
async def download_official_document_pdf(pdf_filename: str):
    """
    Downloads a specific official business document PDF.
    """
    docs_dir = Path(settings.DOCUMENTS_DIR)
    workspace_root = Path(settings.DOCUMENTS_DIR).parents[1]
    exports_dir = workspace_root / "exports" / "pdf" / "documents"
    pdf_path = exports_dir / pdf_filename

    if not pdf_path.exists():
        # Check if source md exists to generate on-demand
        md_name = pdf_filename.replace(".pdf", ".md")
        md_path = docs_dir / md_name
        if md_path.exists():
            _pdf_generator.convert_markdown_to_pdf(str(md_path), str(pdf_path))
        else:
            raise HTTPException(status_code=404, detail="Document PDF not found.")

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=pdf_filename,
        headers={"Content-Disposition": f"attachment; filename={pdf_filename}"}
    )
