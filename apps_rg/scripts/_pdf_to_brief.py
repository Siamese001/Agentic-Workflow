"""One-shot: extract Brown & Brown briefing PDF -> _interactive_brief.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pypdf

PDF = Path(r"C:\Users\amita\Downloads\Brown & Brown - Resume Prep SVP IT.pdf")
OUT = Path("apps_rg/scripts/_interactive_brief.json")
COMPANY = "Brown & Brown"


def main() -> int:
    if not PDF.exists():
        print(f"FATAL: {PDF} not found", file=sys.stderr)
        return 1
    reader = pypdf.PdfReader(str(PDF))
    pages = [page.extract_text() or "" for page in reader.pages]
    text = "\n\n".join(pages).strip()
    payload = {
        "company": COMPANY,
        "_source": str(PDF),
        "_extractor": "pypdf",
        "freeform_text": text,
        "page_count": len(pages),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"wrote {OUT} ({len(text)} chars from {len(pages)} pages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
