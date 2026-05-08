"""RTC-REQ-001 — Canonical Universe Declared.

Validates that the certification matrix CSV is loadable, non-empty,
and declares a canonical universe of requirements.

W0 implementation per runtime-cert-hardened-w0-7e3c9a.md
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from agentic_core.runtime.prove_requirements.matrix_loader import load_matrix, CANONICAL_CSV_PATH


class TestRTC001CanonicalUniverse:
    """RTC-REQ-001: Canonical universe declared in CSV."""

    def test_canonical_csv_exists(self) -> None:
        """CSV file exists at canonical path."""
        assert CANONICAL_CSV_PATH.exists(), f"Canonical CSV not found at {CANONICAL_CSV_PATH}"

    def test_canonical_csv_is_readable(self) -> None:
        """CSV is readable and parseable."""
        rows = load_matrix()
        assert isinstance(rows, list)

    def test_canonical_csv_non_empty(self) -> None:
        """CSV contains at least one requirement row."""
        rows = load_matrix()
        assert len(rows) > 0, "Matrix has no requirements"

    def test_minimum_row_count(self) -> None:
        """Matrix has ≥20 rows (hardened matrix scope)."""
        rows = load_matrix()
        assert len(rows) >= 20, f"Expected ≥20 rows, got {len(rows)}"

    def test_required_columns_present(self) -> None:
        """CSV has required columns: req_id, title, proof_depth."""
        with open(CANONICAL_CSV_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
        
        required = ["req_id", "title", "proof_depth"]
        for col in required:
            assert col in headers, f"Required column '{col}' missing from CSV"

    def test_all_rows_have_req_id(self) -> None:
        """Every row has a non-empty req_id."""
        rows = load_matrix()
        for i, row in enumerate(rows, 1):
            assert row.get("req_id"), f"Row {i} missing req_id"

    def test_req_id_format(self) -> None:
        """req_id follows RTC-REQ-NNN pattern."""
        rows = load_matrix()
        for row in rows:
            req_id = row.get("req_id", "")
            assert req_id.startswith("RTC-REQ-"), f"Invalid req_id format: {req_id}"


class TestRTC001MatrixLoaderAPI:
    """Matrix loader API contract tests."""

    def test_load_matrix_returns_list_of_dict(self) -> None:
        """load_matrix() returns List[Dict[str, str]]."""
        rows = load_matrix()
        assert all(isinstance(r, dict) for r in rows)

    def test_load_matrix_idempotent(self) -> None:
        """Multiple calls return identical data."""
        rows1 = load_matrix()
        rows2 = load_matrix()
        assert rows1 == rows2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
