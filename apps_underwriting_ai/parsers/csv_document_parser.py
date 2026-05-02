"""CSV evidence-table parser.

Parses a CSV file whose first row is a header. Populates
:attr:`ParsedDocument.fields` with:
  - ``columns``: tuple of column names (preserves order)
  - ``rows``: list of dicts (one per data row)
  - ``row_count``: total data rows

The ``text`` field is a deterministic ``csv``-dialect rendering so
downstream LLM consumers can ingest the content verbatim.
"""
from __future__ import annotations

import csv
import io
from pathlib import Path

from apps_underwriting_ai.parsers.document_parser import (
    DocumentParseError,
    DocumentParser,
    ParsedDocument,
)

_MAX_ROWS = 10_000
"""Defensive ceiling — refuse CSVs larger than this to avoid DoS."""


class CsvDocumentParser(DocumentParser):
    """Parse a CSV file into a :class:`ParsedDocument`.

    Contract:
      - CSV MUST have a header row. Header-less CSVs raise
        :class:`DocumentParseError`.
      - Empty CSVs (header only) parse successfully with ``rows=[]``.
      - Row count capped at ``_MAX_ROWS``; exceeding that raises
        :class:`DocumentParseError`.
    """

    name = "csv"
    extensions = (".csv",)

    def parse(
        self,
        source: bytes | Path,
        *,
        document_id: str,
    ) -> ParsedDocument:
        raw = self._read_bytes(source)
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise DocumentParseError(f"CSV not utf-8: {exc}") from exc
        reader = csv.reader(io.StringIO(text))
        try:
            header = next(reader)
        except StopIteration as exc:
            raise DocumentParseError("empty CSV (no header row)") from exc
        if not header or not any(col.strip() for col in header):
            raise DocumentParseError("CSV header row is empty or whitespace-only")
        columns = tuple(col.strip() for col in header)
        rows: list[dict[str, str]] = []
        for i, row in enumerate(reader, start=2):
            if i - 1 > _MAX_ROWS:
                raise DocumentParseError(f"CSV exceeds row ceiling of {_MAX_ROWS}")
            if not row:
                continue
            # Pad / truncate to header width
            padded = list(row) + [""] * (len(columns) - len(row))
            rows.append({columns[j]: padded[j] for j in range(len(columns))})
        return ParsedDocument(
            document_id=document_id,
            parser_name=self.name,
            text=text,
            fields={
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
            },
            page_count=0,
            notes=(f"{len(columns)} columns, {len(rows)} rows",),
        )
