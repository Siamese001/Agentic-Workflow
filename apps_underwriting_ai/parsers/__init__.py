"""Document parsers for apps_underwriting_ai.

Skeleton-stage scope: text + structured-field extraction from JSON, CSV,
and text-only PDFs. Image-PDF OCR and prompt-injection defences are
deferred per plan ``apps-underwriting-feature-complete-aa79a7`` scope
boundary.

Public API:
  - :class:`DocumentParser` — abstract base
  - :class:`ParsedDocument` — shared output contract
  - :class:`DocumentParseError`, :class:`OptionalDependencyMissing` — errors
  - :class:`JsonDocumentParser`, :class:`CsvDocumentParser`,
    :class:`PdfTextParser` — concrete parsers
  - :func:`resolve_parser`, :func:`registered_extensions` — registry
"""
from __future__ import annotations

from apps_underwriting_ai.parsers.csv_document_parser import CsvDocumentParser
from apps_underwriting_ai.parsers.document_parser import (
    DocumentParseError,
    DocumentParser,
    OptionalDependencyMissing,
    ParsedDocument,
    register_parser,
    registered_extensions,
    resolve_parser,
)
from apps_underwriting_ai.parsers.json_document_parser import JsonDocumentParser
from apps_underwriting_ai.parsers.pdf_text_parser import PdfTextParser

# Auto-register concrete parsers on package import.
register_parser(JsonDocumentParser())
register_parser(CsvDocumentParser())
register_parser(PdfTextParser())

__all__ = [
    "CsvDocumentParser",
    "DocumentParseError",
    "DocumentParser",
    "JsonDocumentParser",
    "OptionalDependencyMissing",
    "ParsedDocument",
    "PdfTextParser",
    "register_parser",
    "registered_extensions",
    "resolve_parser",
]
