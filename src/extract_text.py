"""
Sunbeams AI Worksheet Generator — Text Extraction Module
==========================================================
Task 1: Data Pipeline & Text Extraction

Extracts text from Sunbeams textbook PDFs using pdfplumber (primary)
with PyPDF2 as a fallback engine. Includes a fix for the classic
Urdu/RTL word-order scrambling problem seen in PDF text layers.

Usage:
    from extract_text import extract_pdf
    result = extract_pdf("book.pdf")
"""

import pdfplumber
import PyPDF2


def extract_with_pdfplumber(path):
    """Primary extraction engine. Returns list of per-page text strings."""
    pages_text = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            pages_text.append(text)
    return pages_text


def extract_with_pypdf2(path):
    """Fallback engine — used only if pdfplumber returns nothing."""
    pages_text = []
    with open(path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text = page.extract_text() or ""
            pages_text.append(text)
    return pages_text


def fix_urdu_word_order(text):
    """
    Fixes the common RTL word-order bug where pdfplumber/PyPDF2 extract
    Urdu text in left-to-right visual order instead of right-to-left
    reading order. Reverses word order per line.

    NOTE: This only fixes word ORDER. It cannot fix broken text caused
    by PDFs that embed Urdu using non-standard/custom font encodings
    (common in Nastaliq fonts) — see README for details.
    """
    fixed_lines = []
    for line in text.split("\n"):
        words = line.split()
        fixed_lines.append(" ".join(reversed(words)))
    return "\n".join(fixed_lines)


def is_scanned_image_pdf(path, min_chars=15):
    """
    Detects whether a PDF is a real text PDF or a scanned image
    (e.g. photographed/CamScanned textbook pages with no text layer).
    Checks the first page and a middle page.
    """
    with pdfplumber.open(path) as pdf:
        n = len(pdf.pages)
        if n == 0:
            return True
        first = (pdf.pages[0].extract_text() or "").strip()
        mid = (pdf.pages[n // 2].extract_text() or "").strip()
        return len(first) < min_chars and len(mid) < min_chars


def extract_pdf(path, subject_is_urdu=False):
    """
    Full extraction pipeline for one PDF.
    Returns a dict: {
        "n_pages": int,
        "is_scanned": bool,
        "engine_used": str,
        "pages": [str, ...]
    }
    """
    scanned = is_scanned_image_pdf(path)

    pages = extract_with_pdfplumber(path)
    engine = "pdfplumber"

    # if pdfplumber got nothing meaningful, try PyPDF2 as a fallback
    if all(len(p.strip()) < 15 for p in pages):
        pages2 = extract_with_pypdf2(path)
        if any(len(p.strip()) >= 15 for p in pages2):
            pages = pages2
            engine = "PyPDF2"

    if subject_is_urdu:
        pages = [fix_urdu_word_order(p) for p in pages]

    return {
        "n_pages": len(pages),
        "is_scanned": scanned,
        "engine_used": engine,
        "pages": pages,
    }


if __name__ == "__main__":
    import sys
    result = extract_pdf(sys.argv[1], subject_is_urdu="urdu" in sys.argv[1].lower())
    print(f"Pages: {result['n_pages']} | Scanned: {result['is_scanned']} | Engine: {result['engine_used']}")
    print(result["pages"][0][:300])
