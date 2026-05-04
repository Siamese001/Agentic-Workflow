"""Structured-JSON document parser.

Accepts a JSON object at the document root. Populates
:attr:`ParsedDocument.fields` with the top-level keys and synthesizes a
human-readable ``text`` rendering for downstream consumers.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps_underwriting_ai.engines.parsers.document_parser import (
    DocumentParseError,
    DocumentParser,
    ParsedDocument,
)


class JsonDocumentParser(DocumentParser):
    """Parse a JSON object into a :class:`ParsedDocument`.

    Contract:
      - Top-level value MUST be a JSON object (not a list / scalar). Non-object
        inputs raise :class:`DocumentParseError`.
      - Nested structures pass through untouched into ``fields``.
      - Generated ``text`` is a deterministic ``key: value`` rendering.
    """

    name = "json"
    extensions = (".json",)

    def parse(
        self,
        source: bytes | Path,
        *,
        document_id: str,
    ) -> ParsedDocument:
        raw = self._read_bytes(source)
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise DocumentParseError(f"invalid JSON: {exc}") from exc
        if not isinstance(payload, dict):
            raise DocumentParseError(
                f"top-level JSON value must be an object, got {type(payload).__name__}"
            )
        fields: dict[str, Any] = dict(payload)
        text = _render_text(fields)
        return ParsedDocument(
            document_id=document_id,
            parser_name=self.name,
            text=text,
            fields=fields,
            page_count=0,
            notes=(f"{len(fields)} top-level keys",),
        )


def _render_text(fields: dict[str, Any]) -> str:
    """Deterministic key-sorted key:value rendering."""
    lines = []
    for key in sorted(fields):
        value = fields[key]
        if isinstance(value, (dict, list)):
            lines.append(f"{key}: {json.dumps(value, sort_keys=True, default=str)}")
        else:
            lines.append(f"{key}: {value}")
    return "\n".join(lines)
