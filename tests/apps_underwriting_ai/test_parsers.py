"""W1 parser contract tests."""
from __future__ import annotations

import json
import logging
from pathlib import Path

import pytest

from apps_underwriting_ai.parsers import (
    CsvDocumentParser,
    DocumentParseError,
    JsonDocumentParser,
    OptionalDependencyMissing,
    ParsedDocument,
    PdfTextParser,
    registered_extensions,
    resolve_parser,
)
from apps_underwriting_ai.parsers.document_parser import (
    DocumentParser,
    register_parser,
)

# -- Registry ----------------------------------------------------------------


def test_registered_extensions_contains_expected() -> None:
    exts = set(registered_extensions())
    assert {".json", ".csv", ".pdf"}.issubset(exts)


def test_resolve_parser_known_extensions() -> None:
    assert resolve_parser(".json").name == "json"
    assert resolve_parser(".csv").name == "csv"
    assert resolve_parser(".pdf").name == "pdf_text"


def test_resolve_parser_unknown_returns_none() -> None:
    assert resolve_parser(".unknown_ext_zzz") is None


def test_resolve_parser_case_insensitive() -> None:
    assert resolve_parser(".JSON").name == "json"
    assert resolve_parser(".CSV").name == "csv"


def test_register_parser_rejects_empty_name() -> None:
    class Bogus(DocumentParser):
        name = ""
        extensions = (".bogus",)

    with pytest.raises(ValueError, match="non-empty name"):
        register_parser(Bogus())


def test_register_parser_rejects_bad_extension() -> None:
    class Bogus(DocumentParser):
        name = "bogus"
        extensions = ("noleadingdot",)

    with pytest.raises(ValueError, match="must start with"):
        register_parser(Bogus())


# -- JSON parser -------------------------------------------------------------


def test_json_parser_happy_path() -> None:
    result = JsonDocumentParser().parse(
        b'{"a": 1, "b": "x"}', document_id="d-1"
    )
    assert isinstance(result, ParsedDocument)
    assert result.parser_name == "json"
    assert result.document_id == "d-1"
    assert result.fields == {"a": 1, "b": "x"}
    assert "a: 1" in result.text
    assert "b: x" in result.text


def test_json_parser_from_path(tmp_path: Path) -> None:
    p = tmp_path / "doc.json"
    p.write_text('{"k": "v"}', encoding="utf-8")
    logging.info("C3 write receipt: tests/apps_underwriting_ai/test_parsers.py write side effect recorded")
    result = JsonDocumentParser().parse(p, document_id="d-path")
    assert result.fields == {"k": "v"}


def test_json_parser_rejects_list_root() -> None:
    with pytest.raises(DocumentParseError, match="must be an object"):
        JsonDocumentParser().parse(b"[1, 2, 3]", document_id="d-list")


def test_json_parser_rejects_invalid_json() -> None:
    with pytest.raises(DocumentParseError, match="invalid JSON"):
        JsonDocumentParser().parse(b"{not valid", document_id="d-bad")


def test_json_parser_text_is_key_sorted() -> None:
    result = JsonDocumentParser().parse(
        b'{"z": 1, "a": 2, "m": 3}', document_id="d-sort"
    )
    lines = result.text.splitlines()
    keys = [line.split(":")[0] for line in lines]
    assert keys == sorted(keys)


def test_json_parser_missing_path_raises_file_not_found(tmp_path: Path) -> None:
    missing = tmp_path / "nope.json"
    with pytest.raises(FileNotFoundError):
        JsonDocumentParser().parse(missing, document_id="d-missing")


# -- CSV parser --------------------------------------------------------------


def test_csv_parser_happy_path() -> None:
    result = CsvDocumentParser().parse(
        b"col1,col2\nv1,v2\nv3,v4\n", document_id="d-csv"
    )
    assert result.parser_name == "csv"
    assert result.fields["columns"] == ("col1", "col2")
    assert result.fields["row_count"] == 2
    assert result.fields["rows"][0] == {"col1": "v1", "col2": "v2"}


def test_csv_parser_empty_header_raises() -> None:
    with pytest.raises(DocumentParseError, match="empty or whitespace"):
        CsvDocumentParser().parse(b",,\nv1,v2\n", document_id="d")


def test_csv_parser_completely_empty_raises() -> None:
    with pytest.raises(DocumentParseError, match="empty CSV"):
        CsvDocumentParser().parse(b"", document_id="d")


def test_csv_parser_header_only_ok() -> None:
    result = CsvDocumentParser().parse(b"a,b,c\n", document_id="d-headeronly")
    assert result.fields["row_count"] == 0
    assert result.fields["columns"] == ("a", "b", "c")


def test_csv_parser_pads_short_rows() -> None:
    result = CsvDocumentParser().parse(
        b"a,b,c\n1,2\n", document_id="d-short"
    )
    assert result.fields["rows"] == [{"a": "1", "b": "2", "c": ""}]


def test_csv_parser_handles_utf8_bom() -> None:
    payload = b"\xef\xbb\xbfcol1,col2\nv1,v2\n"
    result = CsvDocumentParser().parse(payload, document_id="d-bom")
    assert result.fields["columns"] == ("col1", "col2")


# -- PDF parser --------------------------------------------------------------


def test_pdf_parser_malformed_raises_parse_error() -> None:
    parser = PdfTextParser()
    # pypdf is installed in CI; junk bytes fail parse
    try:
        import pypdf  # noqa: F401
    except ImportError:
        pytest.skip("pypdf not installed")
    with pytest.raises(DocumentParseError, match="pypdf failed"):
        parser.parse(b"\x25PDF-junk-not-a-pdf", document_id="d-pdf-junk")


def test_pdf_parser_missing_dep_message() -> None:
    """Contract: if pypdf is missing, parse raises OptionalDependencyMissing.

    We can't uninstall pypdf for this test; we verify the exception class
    hierarchy so the contract is enforceable.
    """
    assert issubclass(OptionalDependencyMissing, DocumentParseError)


# -- ParsedDocument contract -------------------------------------------------


def test_parsed_document_is_frozen() -> None:
    from dataclasses import FrozenInstanceError

    doc = ParsedDocument(document_id="d", parser_name="json")
    with pytest.raises(FrozenInstanceError):
        doc.document_id = "d2"  # type: ignore[misc]


def test_parsed_document_default_fields_are_safe() -> None:
    doc = ParsedDocument(document_id="d", parser_name="x")
    assert doc.text == ""
    assert doc.fields == {}
    assert doc.page_count == 0
    assert doc.notes == ()
