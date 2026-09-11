from __future__ import annotations

import html
from io import BytesIO
from pathlib import Path
import re
import unicodedata

from arabic_reshaper import reshape
from bidi.algorithm import get_display
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

BASE_DIR = Path(__file__).resolve().parent
FONT_DIR = BASE_DIR / "assets" / "fonts"
URDU_FONT = FONT_DIR / "NotoNastaliqUrdu-Regular.ttf"
URDU_FONT_NAME = "SunbeamsUrdu"

NAVY = colors.HexColor("#0B2E5B")
GOLD = colors.HexColor("#F4B400")
INK = colors.HexColor("#1A1A1A")
MUTED = colors.HexColor("#667085")
BORDER = colors.HexColor("#D9DCE1")
PALE_GOLD = colors.HexColor("#FFF9E8")


def _register_fonts() -> str:
    """Register the bundled Urdu font, or use a system fallback if assets are missing."""
    if URDU_FONT.exists():
        if URDU_FONT_NAME not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(URDU_FONT_NAME, str(URDU_FONT)))
        return URDU_FONT_NAME
    fallback = "/usr/share/fonts/opentype/fonts-hosny-amiri/Amiri-Regular.ttf"
    if Path(fallback).exists():
        if "SunbeamsArabicFallback" not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont("SunbeamsArabicFallback", fallback))
        return "SunbeamsArabicFallback"
    return "Helvetica"


def contains_rtl(text: str) -> bool:
    return bool(re.search(r"[\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff]", text or ""))


def shape_rtl(text: str) -> str:
    """Shape Arabic-script text so ReportLab's canvas renders connected glyphs correctly."""
    return get_display(reshape(text))


def clean_text(text: str) -> str:
    """Remove user-entered markup and normalize characters before PDF rendering."""
    value = html.unescape(str(text or ""))
    value = re.sub(r"<\s*br\s*/?\s*>", "\n", value, flags=re.IGNORECASE)
    value = re.sub(r"<[^>]+>", "", value)
    replacements = {
        "\u00a0": " ", "\u00b7": "|", "\u2022": "-", "\u2013": "-", "\u2014": "-",
        "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"', "\u2026": "...",
        "\u200b": "", "\ufeff": "",
    }
    value = "".join(replacements.get(char, char) for char in value)
    value = unicodedata.normalize("NFC", value)
    return value.strip()


def _rtl_paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    shaped = shape_rtl(clean_text(text))
    rtl_style = ParagraphStyle(
        "RtlBody",
        parent=style,
        fontName=_register_fonts(),
        alignment=TA_RIGHT,
        leading=style.fontSize * 2.1,
        wordWrap="RTL",
    )
    return Paragraph(shaped.replace("\n", "<br/>") , rtl_style)


def _body_paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    if contains_rtl(text):
        return _rtl_paragraph(text, style)
    safe = html.escape(clean_text(text), quote=False)
    return Paragraph(safe.replace("\n", "<br/>"), style)


def _header_footer(canvas, doc):
    canvas.saveState()
    width, height = A4
    canvas.setFillColor(NAVY)
    canvas.rect(0, height - 13 * mm, width, 13 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(18 * mm, height - 8.5 * mm, "SUNBEAMS SCHOOL SYSTEM")
    canvas.setFillColor(GOLD)
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(width - 18 * mm, height - 8.5 * mm, "Worksheet Studio")
    canvas.setStrokeColor(BORDER)
    canvas.line(18 * mm, 15 * mm, width - 18 * mm, 15 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(18 * mm, 9 * mm, "Learn · Grow · Shine")
    canvas.drawRightString(width - 18 * mm, 9 * mm, f"Page {doc.page}")
    canvas.restoreState()


def build_worksheet_pdf(
    questions: list[str],
    subject: str,
    grade: str,
    topic: str,
    difficulty: str,
    include_urdu: bool = True,
) -> bytes:
    """Return a classroom-ready worksheet PDF as bytes."""
    urdu_font = _register_fonts()
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=22 * mm,
        bottomMargin=21 * mm,
        title=f"Sunbeams Worksheet - {subject} {grade}",
        author="Sunbeams Worksheet Studio",
    )
    styles = getSampleStyleSheet()
    title = ParagraphStyle("Title", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=NAVY, alignment=TA_CENTER, spaceAfter=4)
    meta = ParagraphStyle("Meta", parent=styles["Normal"], fontName="Helvetica", fontSize=9, leading=12, textColor=MUTED, alignment=TA_CENTER)
    section = ParagraphStyle("Section", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=NAVY, spaceBefore=8, spaceAfter=5)
    body = ParagraphStyle("Body", parent=styles["BodyText"], fontName="Helvetica", fontSize=10.5, leading=15, textColor=INK, spaceAfter=5)
    question = ParagraphStyle("Question", parent=body, leftIndent=2 * mm, firstLineIndent=0)
    small = ParagraphStyle("Small", parent=body, fontSize=9, leading=12, textColor=MUTED)

    story = [Spacer(1, 4 * mm), Paragraph("WORKSHEET", title), _body_paragraph(f"{subject} | {grade} | {topic or 'General revision'} | {difficulty}", meta), Spacer(1, 7 * mm)]
    story.append(Table([[Paragraph("Name: ______________________________", body), Paragraph("Date: ______________", body)]], colWidths=[105 * mm, 60 * mm], style=TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.4, BORDER)])))
    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph("Instructions", section))
    story.append(Paragraph("Read each question carefully and write your answer in the space provided.", small))

    for index, text in enumerate(questions, 1):
        q = _body_paragraph(f"{index}. {text}", question)
        answer_lines = "\n".join(["____________________________________________________________"] * (2 if len(text) > 85 else 1))
        story.append(KeepTogether([q, Spacer(1, 1.5 * mm), _body_paragraph(answer_lines, small), Spacer(1, 3 * mm)]))

    if include_urdu:
        story.append(Spacer(1, 4 * mm))
        story.append(Paragraph("بچوں کے لیے اردو مشق", section))
        urdu_samples = [
            "سوال: درست جواب منتخب کریں۔ سورج کہاں سے طلوع ہوتا ہے؟",
            "خالی جگہ پُر کریں: پودوں کو بڑھنے کے لیے پانی اور روشنی کی ضرورت ہوتی ہے۔",
            "اپنے کلاس روم کو صاف رکھنے کے دو طریقے لکھیں۔",
        ]
        for index, text in enumerate(urdu_samples, 1):
            story.append(_rtl_paragraph(f"{index}. {text}", body))
            story.append(Spacer(1, 2 * mm))

    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    return buffer.getvalue()


def build_answer_key_pdf(
    questions: list[str],
    subject: str,
    grade: str,
    topic: str,
    answers: list[str] | None = None,
) -> bytes:
    """Return a teacher answer-key PDF as bytes."""
    _register_fonts()
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm, topMargin=22 * mm, bottomMargin=21 * mm, title=f"Answer Key - {subject} {grade}")
    styles = getSampleStyleSheet()
    title = ParagraphStyle("KeyTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=NAVY, alignment=TA_CENTER, spaceAfter=4)
    meta = ParagraphStyle("KeyMeta", parent=styles["Normal"], fontName="Helvetica", fontSize=9, leading=12, textColor=MUTED, alignment=TA_CENTER)
    body = ParagraphStyle("KeyBody", parent=styles["BodyText"], fontName="Helvetica", fontSize=10, leading=14, textColor=INK, spaceAfter=6)
    story = [Spacer(1, 4 * mm), Paragraph("TEACHER ANSWER KEY", title), _body_paragraph(f"{subject} | {grade} | {topic or 'General revision'}", meta), Spacer(1, 8 * mm)]
    rows = [[Paragraph("#", body), Paragraph("Question", body), Paragraph("Suggested answer", body)]]
    answers = answers or ["Review learner response"] * len(questions)
    for index, (question_text, answer) in enumerate(zip(questions, answers), 1):
        q = _body_paragraph(question_text, body)
        a = _body_paragraph(answer, body)
        rows.append([Paragraph(str(index), body), q, a])
    table = Table(rows, colWidths=[10 * mm, 98 * mm, 57 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.45, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE_GOLD]),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(table)
    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    return buffer.getvalue()


if __name__ == "__main__":
    sample = build_worksheet_pdf(["سوال: درست جواب منتخب کریں۔", "Choose the correct answer: 2 + 2 = ?"], "Maths", "Grade 3", "Numbers", "Medium")
    Path("/tmp/sunbeams_smoke_test.pdf").write_bytes(sample)
    print(f"wrote {len(sample)} bytes")
