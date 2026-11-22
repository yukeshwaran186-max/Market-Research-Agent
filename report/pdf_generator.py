"""Professional A4 PDF Report Generator using ReportLab."""

import re
from datetime import datetime
from pathlib import Path
from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)
from reportlab.pdfgen import canvas
from config.settings import PDF_OUTPUT_PATH


class NumberedCanvas(canvas.Canvas):
    """Canvas implementing two-pass evaluation to render dynamic 'Page X of Y' footers."""

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._saved_page_states: list[dict[str, Any]] = []

    def showPage(self) -> None:
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self) -> None:
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int) -> None:
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#718096"))

        # Footer divider line
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.6)
        self.line(54, 45, A4[0] - 54, 45)

        # Footer text and dynamic page count
        footer_text = "MarketResearchAgent | Executive Research Report (Illustrative Data)"
        self.drawString(54, 32, footer_text)
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(A4[0] - 54, 32, page_str)

        self.restoreState()


def _format_inline_markdown(text: str) -> str:
    """Convert basic markdown bold and italic formatting into ReportLab HTML tags."""
    # Convert bold **text** to <b>text</b>
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    # Convert italic *text* to <i>text</i>
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    # Escape ampersands not already part of an entity
    text = re.sub(r"&(?!amp;|lt;|gt;)", "&amp;", text)
    return text


def _parse_markdown_table_rows(table_lines: list[str]) -> list[list[str]]:
    """Parse raw Markdown table lines into rows of stripped strings, skipping divider rows."""
    rows = []
    for line in table_lines:
        line = line.strip()
        if not line.startswith("|"):
            continue
        # Check if line is a markdown separator row (e.g. |:---|---:|)
        cleaned = re.sub(r"[\|\s\:\-]", "", line)
        if not cleaned:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        rows.append(cells)
    return rows


def _build_styled_table(rows: list[list[str]], available_width: float, base_style: ParagraphStyle) -> Table:
    """Construct a clean, professional ReportLab Table flowable from parsed table rows."""
    if not rows:
        return Table([["No tabular data available."]])

    max_cols = max(len(r) for r in rows)
    # Normalize rows to max_cols length
    normalized_rows = []
    for r_idx, row in enumerate(rows):
        padded = row + [""] * (max_cols - len(row))
        formatted_row = []
        for cell in padded:
            cell_text = _format_inline_markdown(cell)
            if r_idx == 0:
                p_style = ParagraphStyle(
                    "TableHeader",
                    parent=base_style,
                    fontName="Helvetica-Bold",
                    fontSize=9,
                    leading=11,
                    textColor=colors.white,
                    alignment=1,  # Center header
                )
            else:
                p_style = ParagraphStyle(
                    "TableCell",
                    parent=base_style,
                    fontName="Helvetica",
                    fontSize=8,
                    leading=10,
                    textColor=colors.HexColor("#2D3748"),
                    alignment=1 if r_idx > 0 else 0,
                )
            formatted_row.append(Paragraph(cell_text, p_style))
        normalized_rows.append(formatted_row)

    col_width = available_width / max_cols
    col_widths = [col_width] * max_cols

    table = Table(normalized_rows, colWidths=col_widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A365D")),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F7FAFC"), colors.HexColor("#EDF2F7")]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
            ]
        )
    )
    return table


def generate_pdf_report(
    content: str,
    query: str = "Tech Sector Q3 Analysis",
    output_path: str | Path | None = None,
) -> Path:
    """Compile Markdown report content into an executive-grade A4 PDF using ReportLab."""
    target_path = Path(output_path or PDF_OUTPUT_PATH)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # Document setup: A4 with 54pt (0.75 in) margins
    doc = SimpleDocTemplate(
        str(target_path),
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    available_width = A4[0] - 108  # Width between left and right margins

    # Typography & Styles
    styles = getSampleStyleSheet()

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#2D3748"),
        spaceAfter=8,
    )

    h1_style = ParagraphStyle(
        "ReportH1",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#1A365D"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        "ReportH2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True,
    )

    h3_style = ParagraphStyle(
        "ReportH3",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#2C5282"),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True,
    )

    bullet_style = ParagraphStyle(
        "ReportBullet",
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4,
    )

    banner_title_style = ParagraphStyle(
        "BannerTitle",
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.white,
    )

    banner_sub_style = ParagraphStyle(
        "BannerSubtitle",
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#E2E8F0"),
    )

    flowables = []

    # 1. Professional Header Banner
    generated_date = datetime.now().strftime("%B %d, %Y")
    banner_content = [
        [Paragraph(f"MARKET RESEARCH REPORT", banner_title_style)],
        [Paragraph(f"Subject: {query} &nbsp;|&nbsp; Date: {generated_date} &nbsp;|&nbsp; Status: Final Executive", banner_sub_style)],
    ]
    banner_table = Table(banner_content, colWidths=[available_width])
    banner_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1A365D")),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                ("LEFTPADDING", (0, 0), (-1, -1), 16),
                ("RIGHTPADDING", (0, 0), (-1, -1), 16),
            ]
        )
    )
    flowables.append(banner_table)
    flowables.append(Spacer(1, 14))

    # 2. Parse Markdown body into flowables
    lines = (content or "").splitlines()
    table_buffer: list[str] = []

    def flush_table() -> None:
        if table_buffer:
            rows = _parse_markdown_table_rows(table_buffer)
            if rows:
                flowables.append(Spacer(1, 4))
                table_flowable = _build_styled_table(rows, available_width, body_style)
                flowables.append(KeepTogether(table_flowable))
                flowables.append(Spacer(1, 8))
            table_buffer.clear()

    for line in lines:
        stripped = line.strip()

        # Handle Markdown table lines
        if stripped.startswith("|"):
            table_buffer.append(stripped)
            continue
        else:
            flush_table()

        if not stripped:
            continue

        # Skip document title or divider if redundant with banner
        if stripped.startswith("# ") and "Market Research Report" in stripped:
            continue
        if stripped.startswith("---"):
            flowables.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#E2E8F0"), spaceAfter=10, spaceBefore=6))
            continue

        # Headings
        if stripped.startswith("### "):
            flowables.append(Paragraph(_format_inline_markdown(stripped[4:]), h3_style))
        elif stripped.startswith("## "):
            flowables.append(Paragraph(_format_inline_markdown(stripped[3:]), h2_style))
        elif stripped.startswith("# "):
            flowables.append(Paragraph(_format_inline_markdown(stripped[2:]), h1_style))
        # Bullet list items
        elif stripped.startswith("- ") or stripped.startswith("* "):
            formatted_item = f"&bull; {_format_inline_markdown(stripped[2:])}"
            flowables.append(Paragraph(formatted_item, bullet_style))
        # Numbered list items
        elif re.match(r"^\d+\.\s+", stripped):
            num_prefix = re.match(r"^\d+\.\s+", stripped).group(0)
            item_text = stripped[len(num_prefix):]
            flowables.append(Paragraph(f"<b>{num_prefix}</b>{_format_inline_markdown(item_text)}", bullet_style))
        # Metadata / block notes
        elif stripped.startswith("**") and stripped.endswith("**"):
            flowables.append(Paragraph(f"<b>{_format_inline_markdown(stripped[2:-2])}</b>", body_style))
        else:
            flowables.append(Paragraph(_format_inline_markdown(stripped), body_style))

    # Flush any remaining table at the end of document
    flush_table()

    # Build PDF with dynamic NumberedCanvas for Page X of Y footers
    doc.build(flowables, canvasmaker=NumberedCanvas)
    return target_path
