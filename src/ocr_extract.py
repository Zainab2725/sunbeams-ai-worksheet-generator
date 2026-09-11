"""
Sunbeams AI Worksheet Generator — OCR Fallback Module
=======================================================
Most Sunbeams PDFs are SCANNED IMAGES (via CamScanner app), not real
text PDFs. pdfplumber/PyPDF2 cannot read text off an image — this
module renders each page to an image and runs Tesseract OCR on it.

Requires:
    - tesseract-ocr (system package)
    - urd.traineddata placed in a tessdata folder (Urdu is NOT bundled
      by default — must be downloaded separately, see README)
    - pip install pytesseract

Usage:
    from ocr_extract import ocr_pdf_page
    text = ocr_pdf_page("book.pdf", page_number=0, lang="urd")
"""

import os
import pdfplumber
import pytesseract
from PIL import Image, ImageOps

TESSDATA_DIR = os.environ.get("TESSDATA_PREFIX", "/home/claude/tessdata")


def ocr_pdf_page(path, page_number, lang="eng", resolution=200, crop_top_fraction=None):
    """
    Renders one PDF page to an image and OCRs it.
    lang: "eng", "urd", or "urd+eng"
    crop_top_fraction: e.g. 0.25 to OCR only the top 25% of the page
                        (useful to isolate a text caption from a large
                        illustration and reduce OCR noise)
    """
    os.environ["TESSDATA_PREFIX"] = TESSDATA_DIR

    with pdfplumber.open(path) as pdf:
        page = pdf.pages[page_number]
        img = page.to_image(resolution=resolution).original

    img = img.convert("L")           # grayscale
    img = ImageOps.autocontrast(img)  # improve contrast

    if crop_top_fraction:
        w, h = img.size
        img = img.crop((0, 0, w, int(h * crop_top_fraction)))

    text = pytesseract.image_to_string(img, lang=lang, config="--psm 6")
    return text.strip()


def ocr_pdf(path, lang="urd", max_pages=None, crop_top_fraction=None):
    """OCRs every page (or up to max_pages) of a scanned PDF."""
    with pdfplumber.open(path) as pdf:
        n = len(pdf.pages)
    n_to_do = min(n, max_pages) if max_pages else n

    results = []
    for i in range(n_to_do):
        text = ocr_pdf_page(path, i, lang=lang, crop_top_fraction=crop_top_fraction)
        results.append(text)
    return results


def easyocr_pdf_page(path, page_number, resolution=100):
    """
    Alternative/stronger OCR engine using EasyOCR (deep-learning based),
    which handles stylised/cursive Urdu fonts noticeably better than
    Tesseract in testing. Returns list of (text, confidence) tuples.

    NOTE: resolution=100 is intentional — EasyOCR is memory-heavy, and
    high-resolution (300dpi) full-page images can exceed available RAM
    in constrained environments. 100dpi was tested and works reliably.
    """
    import easyocr
    with pdfplumber.open(path) as pdf:
        page = pdf.pages[page_number]
        img = page.to_image(resolution=resolution).original.convert("RGB")

    reader = easyocr.Reader(["ur"], gpu=False, verbose=False)
    results = reader.readtext(img, detail=1)
    return [(text, conf) for (_bbox, text, conf) in results]


if __name__ == "__main__":
    import sys
    text = ocr_pdf_page(sys.argv[1], 0, lang="urd")
    print("Tesseract:", text)
    print("EasyOCR:", easyocr_pdf_page(sys.argv[1], 0))
