from __future__ import annotations
import os
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable,
    Image as RLImage
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

# Brand color palette
COLOR_PRIMARY_EMERALD = colors.HexColor("#059669")
COLOR_EMERALD_DARK = colors.HexColor("#047857")
COLOR_EMERALD_LIGHT = colors.HexColor("#ecfdf5")
COLOR_SLATE_DARK = colors.HexColor("#0f172a")
COLOR_SLATE_TEXT = colors.HexColor("#334155")
COLOR_SLATE_MUTED = colors.HexColor("#64748b")
COLOR_BG_CARD = colors.HexColor("#f8fafc")
COLOR_BORDER = colors.HexColor("#cbd5e1")
COLOR_USER_BUBBLE = colors.HexColor("#f1f5f9")
COLOR_BOT_BUBBLE = colors.HexColor("#ecfdf5")
COLOR_ESCALATE_BG = colors.HexColor("#fef2f2")
COLOR_ESCALATE_BORDER = colors.HexColor("#f87171")


class NumberedCanvas(canvas.Canvas):
    """Canvas that computes total pages dynamically for footer page numbers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count: int):
        self.saveState()

        # Header rule
        self.setStrokeColor(COLOR_BORDER)
        self.setLineWidth(0.5)
        self.line(40, 750, 572, 750)

        # Header text
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(COLOR_EMERALD_DARK)
        self.drawString(40, 755, "GASTROTEACHER ACADEMY")
        self.setFont("Helvetica", 8)
        self.setFillColor(COLOR_SLATE_MUTED)
        self.drawRightString(572, 755, "Documento Oficial • Academia Bilingüe")

        # Footer rule
        self.line(40, 45, 572, 45)

        # Footer text
        self.setFont("Helvetica", 8)
        self.setFillColor(COLOR_SLATE_MUTED)
        self.drawString(40, 32, "© 2026 Gastroteacher Academy • PBX: +57 (601) 745-8900 • Bogotá / Medellín")
        page_str = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(572, 32, page_str)

        self.restoreState()


class GastroteacherPDFGenerator:
    """Generates styled PDFs for business knowledge documents and conversation transcripts."""

    def __init__(self, logo_path: Optional[str] = None):
        self.logo_path = logo_path or self._find_logo()
        self.styles = self._setup_styles()

    def _find_logo(self) -> Optional[str]:
        candidates = [
            "backend/data/gastroteacher-logo.png",
            "frontend/Rage_frontend/public/gastroteacher-logo.png",
            "frontend/Rage_frontend/src/assets/gastroteacher-logo.png"
        ]
        for c in candidates:
            if os.path.exists(c):
                return os.path.abspath(c)
        return None

    def _setup_styles(self):
        base = getSampleStyleSheet()

        return {
            "DocTitle": ParagraphStyle(
                "DocTitle",
                parent=base["Heading1"],
                fontName="Helvetica-Bold",
                fontSize=20,
                leading=24,
                textColor=COLOR_SLATE_DARK,
                spaceAfter=6
            ),
            "DocSubtitle": ParagraphStyle(
                "DocSubtitle",
                parent=base["Normal"],
                fontName="Helvetica",
                fontSize=10,
                leading=14,
                textColor=COLOR_SLATE_MUTED,
                spaceAfter=15
            ),
            "H1": ParagraphStyle(
                "H1",
                parent=base["Heading1"],
                fontName="Helvetica-Bold",
                fontSize=15,
                leading=18,
                textColor=COLOR_EMERALD_DARK,
                spaceBefore=14,
                spaceAfter=6,
                keepWithNext=True
            ),
            "H2": ParagraphStyle(
                "H2",
                parent=base["Heading2"],
                fontName="Helvetica-Bold",
                fontSize=12,
                leading=16,
                textColor=COLOR_SLATE_DARK,
                spaceBefore=10,
                spaceAfter=4,
                keepWithNext=True
            ),
            "H3": ParagraphStyle(
                "H3",
                parent=base["Heading3"],
                fontName="Helvetica-Bold",
                fontSize=10.5,
                leading=14,
                textColor=COLOR_EMERALD_DARK,
                spaceBefore=8,
                spaceAfter=3,
                keepWithNext=True
            ),
            "Body": ParagraphStyle(
                "Body",
                parent=base["Normal"],
                fontName="Helvetica",
                fontSize=9.5,
                leading=14,
                textColor=COLOR_SLATE_TEXT,
                spaceAfter=6
            ),
            "Bullet": ParagraphStyle(
                "Bullet",
                parent=base["Normal"],
                fontName="Helvetica",
                fontSize=9.5,
                leading=14,
                textColor=COLOR_SLATE_TEXT,
                leftIndent=14,
                firstLineIndent=-10,
                spaceAfter=4
            ),
            "TableText": ParagraphStyle(
                "TableText",
                parent=base["Normal"],
                fontName="Helvetica",
                fontSize=8.5,
                leading=11,
                textColor=COLOR_SLATE_TEXT
            ),
            "TableHeader": ParagraphStyle(
                "TableHeader",
                parent=base["Normal"],
                fontName="Helvetica-Bold",
                fontSize=9,
                leading=12,
                textColor=colors.white
            ),
            "Callout": ParagraphStyle(
                "Callout",
                parent=base["Normal"],
                fontName="Helvetica-Oblique",
                fontSize=9,
                leading=13,
                textColor=COLOR_SLATE_DARK
            ),
            "UserBadge": ParagraphStyle(
                "UserBadge",
                parent=base["Normal"],
                fontName="Helvetica-Bold",
                fontSize=8.5,
                leading=11,
                textColor=COLOR_SLATE_DARK
            ),
            "BotBadge": ParagraphStyle(
                "BotBadge",
                parent=base["Normal"],
                fontName="Helvetica-Bold",
                fontSize=8.5,
                leading=11,
                textColor=COLOR_EMERALD_DARK
            ),
            "MetaText": ParagraphStyle(
                "MetaText",
                parent=base["Normal"],
                fontName="Helvetica",
                fontSize=7.5,
                leading=10,
                textColor=COLOR_SLATE_MUTED
            )
        }

    def convert_markdown_to_pdf(self, md_file_path: str, output_pdf_path: str) -> str:
        """Converts a single markdown document into a professional PDF."""
        os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)

        with open(md_file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        doc = SimpleDocTemplate(
            output_pdf_path,
            pagesize=letter,
            leftMargin=40,
            rightMargin=40,
            topMargin=55,
            bottomMargin=55
        )

        story = []

        # Document Header Banner
        header_table = self._build_header_banner(
            title="GASTROTEACHER ACADEMY",
            tagline="Official Academic & Business Documentation",
            category="Documento Oficial del Negocio"
        )
        story.append(header_table)
        story.append(Spacer(1, 14))

        # Parse markdown lines into Flowables
        in_table = False
        table_data = []

        for raw_line in lines:
            line = raw_line.strip()

            if not line:
                if in_table and table_data:
                    story.append(self._render_markdown_table(table_data))
                    story.append(Spacer(1, 8))
                    in_table = False
                    table_data = []
                continue

            # Check markdown table row
            if line.startswith("|") and line.endswith("|"):
                if re.match(r'^\|[\s\-:|]+\|$', line):
                    continue  # separator row
                cols = [c.strip() for c in line.split("|")[1:-1]]
                table_data.append(cols)
                in_table = True
                continue
            elif in_table and table_data:
                story.append(self._render_markdown_table(table_data))
                story.append(Spacer(1, 8))
                in_table = False
                table_data = []

            # Headings
            if line.startswith("# "):
                title_text = line[2:].strip()
                story.append(Paragraph(title_text, self.styles["DocTitle"]))
                story.append(HRFlowable(width="100%", thickness=1.5, color=COLOR_PRIMARY_EMERALD, spaceBefore=4, spaceAfter=10))
            elif line.startswith("## "):
                story.append(Paragraph(line[3:].strip(), self.styles["H1"]))
            elif line.startswith("### "):
                story.append(Paragraph(line[4:].strip(), self.styles["H2"]))
            elif line.startswith("#### "):
                story.append(Paragraph(line[5:].strip(), self.styles["H3"]))

            # Bullet points
            elif line.startswith("- ") or line.startswith("* "):
                bullet_text = self._format_inline_markdown(line[2:].strip())
                story.append(Paragraph(f"• {bullet_text}", self.styles["Bullet"]))

            # Numbered list
            elif re.match(r'^\d+\.\s', line):
                num_text = self._format_inline_markdown(re.sub(r'^\d+\.\s', '', line).strip())
                prefix = re.match(r'^(\d+\.)', line).group(1)
                story.append(Paragraph(f"<b>{prefix}</b> {num_text}", self.styles["Bullet"]))

            # Blockquote / Callout
            elif line.startswith(">"):
                callout_text = self._format_inline_markdown(line[1:].strip())
                callout_box = self._render_callout_box(callout_text)
                story.append(callout_box)
                story.append(Spacer(1, 6))

            # Regular paragraph
            else:
                body_text = self._format_inline_markdown(line)
                story.append(Paragraph(body_text, self.styles["Body"]))

        if in_table and table_data:
            story.append(self._render_markdown_table(table_data))

        # Build Document
        doc.build(story, canvasmaker=NumberedCanvas)
        return output_pdf_path

    def convert_conversation_to_pdf(
        self,
        messages: List[Dict[str, Any]],
        session_id: str,
        output_pdf_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Converts a chat conversation history into a beautifully styled transcript PDF."""
        os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)

        doc = SimpleDocTemplate(
            output_pdf_path,
            pagesize=letter,
            leftMargin=40,
            rightMargin=40,
            topMargin=55,
            bottomMargin=55
        )

        story = []

        # Conversation Header Banner
        header_table = self._build_header_banner(
            title="REGISTRO DE CONVERSACIÓN / CHAT TRANSCRIPT",
            tagline=f"ID de Sesión: {session_id} • Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            category="Atención al Cliente con IA & RAG"
        )
        story.append(header_table)
        story.append(Spacer(1, 10))

        # Session Metadata Summary Card
        meta_table = self._build_session_metadata_card(session_id, len(messages), metadata)
        story.append(meta_table)
        story.append(Spacer(1, 14))

        story.append(Paragraph("Historial de Interacción:", self.styles["H2"]))
        story.append(HRFlowable(width="100%", thickness=1, color=COLOR_BORDER, spaceBefore=2, spaceAfter=10))

        # Iterate through messages
        for i, msg in enumerate(messages):
            role = msg.get("role", "user").lower()
            text = msg.get("content") or msg.get("text") or msg.get("response") or ""
            is_escalated = msg.get("is_escalated", False)
            sources = msg.get("sources", [])
            latency_ms = msg.get("latency_ms", 0.0)
            tokens = msg.get("token_usage", {})

            bubble = self._build_chat_bubble(
                index=i + 1,
                role=role,
                text=text,
                is_escalated=is_escalated,
                sources=sources,
                latency_ms=latency_ms,
                tokens=tokens
            )
            story.append(bubble)
            story.append(Spacer(1, 8))

        doc.build(story, canvasmaker=NumberedCanvas)
        return output_pdf_path

    def _format_inline_markdown(self, text: str) -> str:
        """Converts bold and italic markdown to HTML tags for ReportLab Paragraphs."""
        # Bold **text**
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        # Italic *text*
        text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
        # Inline code `code`
        text = re.sub(r'`(.*?)`', r'<font face="Courier" color="#047857"><b>\1</b></font>', text)
        return text

    def _build_header_banner(self, title: str, tagline: str, category: str) -> Table:
        logo_cell = ""
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                logo_cell = RLImage(self.logo_path, width=42, height=42)
            except Exception:
                logo_cell = ""

        title_p = Paragraph(f"<b>{title}</b>", self.styles["H2"])
        tagline_p = Paragraph(tagline, self.styles["MetaText"])
        category_p = Paragraph(f"<b>{category.upper()}</b>", self.styles["MetaText"])

        data = [
            [logo_cell, title_p, category_p],
            ["", tagline_p, ""]
        ]

        t = Table(data, colWidths=[48, 350, 134])
        t.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('SPAN', (0, 0), (0, 1)),
            ('ALIGN', (2, 0), (2, 1), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
        ]))
        return t

    def _build_session_metadata_card(self, session_id: str, message_count: int, metadata: Optional[Dict[str, Any]]) -> Table:
        data = [
            [
                Paragraph("<b>Canal de Origen:</b> Web / API", self.styles["MetaText"]),
                Paragraph(f"<b>Total Mensajes:</b> {message_count}", self.styles["MetaText"]),
                Paragraph("<b>Motor RAG:</b> ChromaDB + Embeddings", self.styles["MetaText"]),
                Paragraph("<b>Estado:</b> Procesado ✓", self.styles["MetaText"])
            ]
        ]
        t = Table(data, colWidths=[133, 133, 133, 133])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), COLOR_BG_CARD),
            ('BOX', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        return t

    def _render_callout_box(self, text: str) -> Table:
        p = Paragraph(f"💡 {text}", self.styles["Callout"])
        t = Table([[p]], colWidths=[532])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), COLOR_EMERALD_LIGHT),
            ('BOX', (0, 0), (-1, -1), 1, COLOR_PRIMARY_EMERALD),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        return t

    def _render_markdown_table(self, raw_data: List[List[str]]) -> Table:
        if not raw_data:
            return Table([[""]])

        formatted = []
        num_cols = len(raw_data[0])

        for r_idx, row in enumerate(raw_data):
            formatted_row = []
            for c in row:
                if r_idx == 0:
                    p = Paragraph(self._format_inline_markdown(c), self.styles["TableHeader"])
                else:
                    p = Paragraph(self._format_inline_markdown(c), self.styles["TableText"])
                formatted_row.append(p)
            formatted.append(formatted_row)

        col_width = 532 / max(1, num_cols)
        t = Table(formatted, colWidths=[col_width] * num_cols)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLOR_SLATE_DARK),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLOR_BG_CARD]),
            ('PADDING', (0, 0), (-1, -1), 5),
        ]))
        return t

    def _build_chat_bubble(
        self,
        index: int,
        role: str,
        text: str,
        is_escalated: bool,
        sources: List[Any],
        latency_ms: float,
        tokens: Dict[str, int]
    ) -> KeepTogether:
        flowables = []

        is_bot = role in ("bot", "assistant", "system")
        bg_color = COLOR_BOT_BUBBLE if is_bot else COLOR_USER_BUBBLE
        border_color = COLOR_PRIMARY_EMERALD if is_bot else COLOR_BORDER

        if is_escalated:
            bg_color = COLOR_ESCALATE_BG
            border_color = COLOR_ESCALATE_BORDER

        # Badge header
        badge_style = self.styles["BotBadge"] if is_bot else self.styles["UserBadge"]
        role_label = "🤖 Asistente Gastroteacher" if is_bot else "👤 Usuario / Estudiante"
        badge_p = Paragraph(f"#{index} {role_label}", badge_style)

        # Meta string
        meta_parts = []
        if latency_ms > 0:
            meta_parts.append(f"⏱️ {latency_ms:.1f} ms")
        if tokens and tokens.get("total_tokens"):
            meta_parts.append(f"🔢 {tokens['total_tokens']} tokens")
        if is_escalated:
            meta_parts.append("⚠️ ESCALADO A HUMANO")

        meta_p = Paragraph(" • ".join(meta_parts) if meta_parts else "", self.styles["MetaText"])

        header_tbl = Table([[badge_p, meta_p]], colWidths=[200, 310])
        header_tbl.setStyle(TableStyle([
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 0),
        ]))

        flowables.append(header_tbl)
        flowables.append(Spacer(1, 4))

        # Message body
        formatted_body = self._format_inline_markdown(text).replace("\n", "<br/>")
        flowables.append(Paragraph(formatted_body, self.styles["Body"]))

        # Source citations
        if sources:
            source_names = []
            for s in sources:
                if isinstance(s, dict):
                    source_names.append(s.get("title") or s.get("source", "Documento"))
                elif hasattr(s, "title"):
                    source_names.append(s.title)
            if source_names:
                flowables.append(Spacer(1, 3))
                src_text = "📚 <b>Fuentes Consultadas:</b> " + ", ".join(source_names[:3])
                flowables.append(Paragraph(src_text, self.styles["MetaText"]))

        bubble_tbl = Table([[flowables]], colWidths=[532])
        bubble_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), bg_color),
            ('BOX', (0, 0), (-1, -1), 1, border_color),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))

        return KeepTogether([bubble_tbl])
