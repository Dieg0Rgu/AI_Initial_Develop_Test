#!/usr/bin/env python3
"""
Gastroteacher PDF Exporter CLI
Exports business markdown documents and chat conversation transcripts to styled PDF reports.
Includes aesthetic SweetAlert terminal UI notifications.
"""

from __future__ import annotations
import os
import sys
import time
import argparse
from pathlib import Path
from typing import List, Dict, Any

# Ensure paths
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = WORKSPACE_ROOT / "backend"
sys.path.insert(0, str(WORKSPACE_ROOT))
sys.path.insert(0, str(BACKEND_DIR))

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

try:
    from app.utils.sweet_alert_console import SweetAlert
    from app.utils.pdf_generator import GastroteacherPDFGenerator
except ImportError:
    from backend.app.utils.sweet_alert_console import SweetAlert
    from backend.app.utils.pdf_generator import GastroteacherPDFGenerator

console = Console()

# Sample realistic conversations to export if no live DB is attached
SAMPLE_CONVERSATIONS = [
    {
        "session_id": "session_inscripcion_precios_es",
        "title": "Consulta de Matrícula y Precios en COP",
        "metadata": {"channel": "web_chat", "user": "Estudiante Interesado", "topic": "Tarifas y Financiación"},
        "messages": [
            {
                "role": "user",
                "content": "¡Hola! Mi nombre es Diego y me gustaría conocer los precios del programa de Gastronomy & Hospitality English.",
                "latency_ms": 0.0
            },
            {
                "role": "assistant",
                "content": "¡Hola, **Diego**! Con gusto te comparto la información oficial de precios y facilidades de pago en Gastroteacher:\n\n- **Gastronomy & Hospitality English**: $1.980.000 COP por el programa completo de 120 horas (o $720.000 COP por módulo individual de 40 horas).\n- **Financiación Directa**: Puedes financiar tu matrícula en hasta 3 cuotas mensuales sin interés.\n- **Promociones Activas**: 10% de descuento por pronto pago y 15% presentando carnet de aliados (SENA, Gato Dumas, Mariano Moreno).\n\n¿Te gustaría programar tu test de nivelación gratuito para iniciar?",
                "is_escalated": False,
                "sources": [
                    {"title": "Gastroteacher Academy - Tarifas, Horarios y Promociones", "source": "02_pricing_schedules_promotions.md"},
                    {"title": "Gastroteacher Academy - Cursos, Modalidades y Niveles", "source": "01_courses_modalities_levels.md"}
                ],
                "latency_ms": 42.5,
                "token_usage": {"prompt_tokens": 310, "completion_tokens": 165, "total_tokens": 475}
            },
            {
                "role": "user",
                "content": "¿Tienen clases los sábados para personas que trabajamos?",
                "latency_ms": 0.0
            },
            {
                "role": "assistant",
                "content": "¡Sí, por supuesto! Contamos con jornada especial para profesionales:\n\n- **Sábados Intensivo**: 8:00 AM a 1:00 PM o 2:00 PM a 7:00 PM.\n- **Domingos Mañana**: 8:30 AM a 1:30 PM (100% online en vivo).\n\nAmbos horarios incluyen acceso completo a las grabaciones y a los talleres prácticos de cocina bilingüe. ¿Prefieres tomarlo en modalidad presencial en Bogotá/Medellín o 100% online?",
                "is_escalated": False,
                "sources": [
                    {"title": "Gastroteacher Academy - Tarifas, Horarios y Promociones", "source": "02_pricing_schedules_promotions.md"}
                ],
                "latency_ms": 38.2,
                "token_usage": {"prompt_tokens": 280, "completion_tokens": 120, "total_tokens": 400}
            }
        ]
    },
    {
        "session_id": "session_escalation_admissions_en",
        "title": "Bilingual Inquiry & International Visa Escalation",
        "metadata": {"channel": "telegram_bot", "user": "Chef Sarah Connor", "topic": "Work Visa & Australian Culinary Exchange"},
        "messages": [
            {
                "role": "user",
                "content": "Hello! I am a sous-chef in Australia and I would like to know if you provide work visa sponsorships along with English certification.",
                "latency_ms": 0.0
            },
            {
                "role": "assistant",
                "content": "Hello! Thank you for contacting Gastroteacher Academy. We prepare our culinary professionals for international certifications such as IELTS and TOEFL, but we do not directly process work visas or immigration sponsorships.\n\nTo assist you with specialized international exchange counseling, your case has been escalated to our senior human admissions counselor:\n- **WhatsApp / Telegram**: +57 310 999 8888\n- **Email**: admisiones@gastroteacher.edu.co\n- **Business Hours**: Monday to Friday 8:00 AM - 7:00 PM (COT)\n\nA human counselor will contact you shortly!",
                "is_escalated": True,
                "sources": [
                    {"title": "Gastroteacher Academy - Inscripciones, Certificaciones y Políticas", "source": "03_enrollments_certifications_policies.md"}
                ],
                "latency_ms": 54.1,
                "token_usage": {"prompt_tokens": 340, "completion_tokens": 140, "total_tokens": 480}
            }
        ]
    }
]


def export_all(
    export_docs: bool = True,
    export_chats: bool = True,
    specific_file: str = None,
    output_dir: str = "exports/pdf"
) -> None:
    start_time = time.perf_counter()
    generator = GastroteacherPDFGenerator()

    out_base = WORKSPACE_ROOT / output_dir
    docs_out = out_base / "documents"
    chats_out = out_base / "conversations"

    os.makedirs(docs_out, exist_ok=True)
    os.makedirs(chats_out, exist_ok=True)

    # Initial Info SweetAlert
    SweetAlert.info(
        title="Iniciando Exportador PDF Gastroteacher",
        text="Generando documentos oficiales y transcripciones de conversaciones en formato PDF de alta calidad.",
        details={
            "Directorio de Destino": str(out_base),
            "Documentos de Negocio": "Activado" if export_docs else "Desactivado",
            "Conversaciones RAG": "Activado" if export_chats else "Desactivado"
        },
        action_button="Procesando..."
    )

    exported_files = []

    # 1. Export Business Markdown Documents
    if export_docs:
        docs_dir = BACKEND_DIR / "data" / "documents"
        if specific_file:
            md_files = [Path(specific_file)]
        else:
            md_files = sorted(list(docs_dir.glob("*.md")))

        with Progress(
            SpinnerColumn("dots", style="bold green"),
            TextColumn("[bold green]{task.description}"),
            BarColumn(complete_style="green", finished_style="bold green"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[green]Compilando Documentos Markdown...", total=len(md_files))

            for md_path in md_files:
                if not md_path.exists():
                    continue

                pdf_name = f"{md_path.stem}.pdf"
                dest_pdf = docs_out / pdf_name

                progress.update(task, description=f"[bold green]Generando {pdf_name}...")
                generator.convert_markdown_to_pdf(str(md_path), str(dest_pdf))

                size_kb = round(os.path.getsize(dest_pdf) / 1024, 1)
                exported_files.append({
                    "type": "📄 Documento Oficial",
                    "name": pdf_name,
                    "size": f"{size_kb} KB",
                    "path": str(dest_pdf.relative_to(WORKSPACE_ROOT))
                })
                progress.advance(task)

    # 2. Export Chat Conversation Transcripts
    if export_chats:
        with Progress(
            SpinnerColumn("dots", style="bold cyan"),
            TextColumn("[bold cyan]{task.description}"),
            BarColumn(complete_style="cyan", finished_style="bold cyan"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Compilando Transcripciones de Chat...", total=len(SAMPLE_CONVERSATIONS))

            for chat in SAMPLE_CONVERSATIONS:
                session_id = chat["session_id"]
                pdf_name = f"{session_id}.pdf"
                dest_pdf = chats_out / pdf_name

                progress.update(task, description=f"[bold cyan]Exportando {pdf_name}...")
                generator.convert_conversation_to_pdf(
                    messages=chat["messages"],
                    session_id=session_id,
                    output_pdf_path=str(dest_pdf),
                    metadata=chat.get("metadata")
                )

                size_kb = round(os.path.getsize(dest_pdf) / 1024, 1)
                exported_files.append({
                    "type": "💬 Conversación RAG",
                    "name": pdf_name,
                    "size": f"{size_kb} KB",
                    "path": str(dest_pdf.relative_to(WORKSPACE_ROOT))
                })
                progress.advance(task)

    elapsed = round(time.perf_counter() - start_time, 2)

    # Summary Table
    table_headers = ["Tipo", "Nombre del Archivo", "Tamaño", "Ubicación Relativa"]
    table_rows = [[f["type"], f["name"], f["size"], f["path"]] for f in exported_files]
    SweetAlert.render_summary_table(
        title="Archivos PDF Generados con Éxito",
        headers=table_headers,
        rows=table_rows,
        subtitle=f"Total de archivos procesados: {len(exported_files)} • Tiempo: {elapsed}s"
    )

    # Success SweetAlert Modal
    SweetAlert.success(
        title="¡Exportación a PDF Completada con Éxito!",
        text=f"Se han exportado {len(exported_files)} archivos PDF con diseño corporativo, encabezados institucionales y paginación oficial.",
        details={
            "📁 Directorio Principal": str(out_base),
            "📄 Documentos Oficiales": f"{docs_out}",
            "💬 Conversaciones / Chats": f"{chats_out}",
            "⏱️ Tiempo de Ejecución": f"{elapsed} segundos"
        },
        action_button="Completado ✓"
    )


def main():
    parser = argparse.ArgumentParser(description="Gastroteacher PDF Exporter CLI")
    parser.add_argument("--all", action="store_true", default=False, help="Exportar tanto documentos como conversaciones")
    parser.add_argument("--docs", action="store_true", default=False, help="Exportar únicamente documentos oficiales markdown")
    parser.add_argument("--chats", action="store_true", default=False, help="Exportar únicamente transcripciones de conversaciones")
    parser.add_argument("--file", type=str, default=None, help="Ruta a un archivo markdown específico")
    parser.add_argument("--out", type=str, default="exports/pdf", help="Directorio destino (default: exports/pdf)")

    args = parser.parse_args()

    # Default to exporting all if no specific filter is given
    if not args.docs and not args.chats:
        do_docs = True
        do_chats = True
    else:
        do_docs = args.docs or args.all
        do_chats = args.chats or args.all

    export_all(
        export_docs=do_docs,
        export_chats=do_chats,
        specific_file=args.file,
        output_dir=args.out
    )


if __name__ == "__main__":
    main()
