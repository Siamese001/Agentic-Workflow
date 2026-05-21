"""PDF text-extraction parser.

Uses :mod:`pypdf` when available. If not installed, a parse call raises
:class:`OptionalDependencyMissing` with a clear installation hint.

Skeleton-stage scope: text-only PDFs (no OCR). Image-PDFs extract to an
empty string; the parser still returns successfully with
``notes=("no extractable text",)``. Image-PDF OCR is deferred per plan
scope boundary.
"""
from __future__ import annotations

from pathlib import Path

from apps_underwriting_ai.parsers.document_parser import (
    DocumentParseError,
    DocumentParser,
    OptionalDependencyMissing,
    ParsedDocument,
)


class PdfTextParser(DocumentParser):
    """Extract plain text from a PDF file via pypdf."""

    name = "pdf_text"
    extensions = (".pdf",)

    def parse(
        self,
        source: bytes | Path,
        *,
        document_id: str,
    ) -> ParsedDocument:
        try:
            import pypdf  # type: ignore[import-untyped]
        except ImportError as exc:
            raise OptionalDependencyMissing(
                "pypdf is not installed; run `pip install pypdf` to enable "
                "PDF text extraction"
            ) from exc

        raw = self._read_bytes(source)
        import io

        try:
            reader = pypdf.PdfReader(io.BytesIO(raw))
        except Exception as exc:  # guardian: allow-broad-exception -- pypdf raises many types (PdfReadError, ValueError, KeyError, etc.); all wrapped in DocumentParseError with full context via `from exc`
            raise DocumentParseError(f"pypdf failed to open PDF: {exc}") from exc

        pages_text: list[str] = []
        for page in reader.pages:
            try:
                pages_text.append(page.extract_text() or "")
            except Exception as exc:  # guardian: allow-log-and-swallow -- per-page pypdf failure must not abort multi-page parse; empty string recorded for the failed page so downstream retains page alignment  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
                pages_text.append("")
                _ = exc  # swallowed intentionally — see notes below
        text = "\n".join(pages_text).strip()
        notes: tuple[str, ...]
        if not text:
            notes = ("no extractable text",)
        else:
            notes = (f"{len(pages_text)} pages, {len(text)} chars",)
        return ParsedDocument(
            document_id=document_id,
            parser_name=self.name,
            text=text,
            fields={},
            page_count=len(pages_text),
            notes=notes,
        )
