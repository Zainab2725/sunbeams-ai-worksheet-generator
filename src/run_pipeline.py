"""
Sunbeams AI Worksheet Generator — Pipeline Runner
===================================================
Runs the extraction pipeline across all PDFs in raw/PA, raw/PB, raw/PC
and writes results + a summary report to extracted/.
"""

import os
import json
import sys

sys.path.insert(0, os.path.dirname(__file__))
from extract_text import extract_pdf, is_scanned_image_pdf  # noqa: E402

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "raw")
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "extracted")

PACKAGES = {
    "PA": "Nursery / Prep-1",
    "PB": "Class 2 / 3",
    "PC": "Class 4 / 5",
}


def guess_subject(filename):
    f = filename.lower()
    if "urdu" in f or "nazra" in f:
        return "Urdu"
    if "math" in f:
        return "Math"
    if "english" in f:
        return "English"
    if "science" in f or "s.st" in f or "sst" in f or "social" in f:
        return "Science/Social Studies"
    if "islamiat" in f or "islamiyat" in f:
        return "Islamiat"
    return "Unknown"


def run():
    summary = []
    for pkg, label in PACKAGES.items():
        pkg_raw = os.path.join(RAW_DIR, pkg)
        pkg_out = os.path.join(OUT_DIR, pkg)
        os.makedirs(pkg_out, exist_ok=True)

        for fname in sorted(os.listdir(pkg_raw)):
            if not fname.lower().endswith(".pdf"):
                continue
            path = os.path.join(pkg_raw, fname)
            subject = guess_subject(fname)
            is_urdu = subject == "Urdu"

            try:
                result = extract_pdf(path, subject_is_urdu=is_urdu)
                status = "SCANNED_IMAGE_NO_TEXT_LAYER" if result["is_scanned"] else "TEXT_EXTRACTED"

                # save extracted text (even if mostly empty, for the record)
                out_name = os.path.splitext(fname)[0].strip().replace(" ", "_") + ".txt"
                out_path = os.path.join(pkg_out, out_name)
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(f"# Source: {fname}\n# Status: {status}\n\n")
                    f.write("\n\n---PAGE BREAK---\n\n".join(result["pages"]))

                summary.append({
                    "package": pkg,
                    "package_label": label,
                    "file": fname,
                    "subject": subject,
                    "pages": result["n_pages"],
                    "status": status,
                    "engine": result["engine_used"],
                })
            except Exception as e:
                summary.append({
                    "package": pkg, "package_label": label, "file": fname,
                    "subject": subject, "pages": None, "status": f"ERROR: {e}", "engine": None,
                })

    with open(os.path.join(OUT_DIR, "summary_report.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # Also write a quick CSV for easy viewing
    import csv
    with open(os.path.join(OUT_DIR, "summary_report.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["package", "package_label", "file", "subject", "pages", "status", "engine"])
        writer.writeheader()
        writer.writerows(summary)

    scanned_count = sum(1 for r in summary if r["status"] == "SCANNED_IMAGE_NO_TEXT_LAYER")
    text_count = sum(1 for r in summary if r["status"] == "TEXT_EXTRACTED")
    print(f"Done. {len(summary)} files processed.")
    print(f"  Scanned image PDFs (no text layer): {scanned_count}")
    print(f"  Real text PDFs: {text_count}")
    return summary


if __name__ == "__main__":
    run()
