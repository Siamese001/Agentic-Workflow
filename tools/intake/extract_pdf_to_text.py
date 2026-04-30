"""Extract a PDF to plain text.

Usage:
    python -m tools.intake.extract_pdf_to_text <pdf_path> [--out <text_path>]

If --out is omitted, prints to stdout. Uses pdfplumber with pypdf fallback,
matching the precedence used by apps_qna.integrations.from_research_brief.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def extract_pdf_text(path: Path) -> str:
    """Extract text from a PDF; pdfplumber preferred, pypdf fallback."""
    try:
        import pdfplumber  # type: ignore[import-untyped]

        with pdfplumber.open(path) as pdf:
            return "\n\n".join(page.extract_text() or "" for page in pdf.pages)
    except ImportError:
        pass
    try:
        from pypdf import PdfReader

        reader = PdfReader(path)
        return "\n\n".join((page.extract_text() or "") for page in reader.pages)
    except ImportError as exc:
        raise RuntimeError(
            "Neither pdfplumber nor pypdf is installed. "
            "`uv pip install pdfplumber` or `uv pip install pypdf`."
        ) from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf_path", type=Path, help="Path to the PDF file")
    parser.add_argument(
        "--out", type=Path, default=None,
        help="Optional output text file. If omitted, prints to stdout.",
    )
    args = parser.parse_args(argv)
    if not args.pdf_path.is_file():
        print(f"NOT FOUND: {args.pdf_path}", file=sys.stderr)
        return 1
    text = extract_pdf_text(args.pdf_path)
    if args.out is None:
        print(text)
    else:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"Wrote {len(text):,} chars to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
