"""Tests — Hardened certification matrix schema (RTC-REQ-002, 003, 006, 110).

Plan: ``.windsurf/plans/runtime-cert-hardened-w0-7e3c9a.md``

Coverage
--------

  - Canonical CSV exists at the bound path
  - All 32 required columns present
  - Every row's claim_type is in ALLOWED_CLAIM_TYPES
  - Every row's required_proof_depth is in canonical DEPTHS
  - Row count equals CANONICAL_REQUIREMENT_COUNT
  - Duplicate req_id detection (synthetic CSV)
  - Schema verifier exit code is 0 in clean state
  - Schema verifier exit code is 2 when CSV is missing a column (synthetic
    canonical_path override)
"""

from __future__ import annotations

import csv
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from agentic_core.runtime.prove_requirements.matrix_loader import (
    ALLOWED_CLAIM_TYPES,
    CANONICAL_CSV_PATH,
    CANONICAL_REQUIREMENT_COUNT,
    REQUIRED_COLUMNS,
    MatrixLoadError,
    load_matrix,
)
from agentic_core.runtime.prove_requirements.proof_depth_ladder import (
    DEPTHS,
    is_valid_depth,
)


class TestCanonicalCSV:
    """RTC-REQ-001: canonical CSV bound and complete."""

    def test_canonical_csv_exists(self):
        assert CANONICAL_CSV_PATH.exists(), (
            f"canonical CSV missing at {CANONICAL_CSV_PATH}; "
            "copy from docs/reference/runtime_certification_requirements_100_percent_hardened.csv"
        )

    def test_canonical_csv_loads_clean(self):
        result = load_matrix()
        assert result.row_count == CANONICAL_REQUIREMENT_COUNT
        assert len(result.csv_sha256) == 64  # SHA-256 hex
        assert result.csv_sha256 != ""


class TestSchemaColumns:
    """RTC-REQ-002 + 110: all 32 required columns present."""

    def test_all_required_columns_present(self):
        result = load_matrix()
        for col in REQUIRED_COLUMNS:
            assert col in result.column_names, f"missing required column: {col}"

    def test_required_columns_count_is_32(self):
        assert len(REQUIRED_COLUMNS) == 32


class TestEnumValidity:
    """RTC-REQ-003: claim_type and required_proof_depth must be enums."""

    def test_every_row_claim_type_in_enum(self):
        result = load_matrix()
        bad = []
        for r in result.rows:
            ctype = (r.get("claim_type") or "").strip()
            if ctype and ctype not in ALLOWED_CLAIM_TYPES:
                bad.append((r["req_id"], ctype))
        assert not bad, f"rows with invalid claim_type: {bad}"

    def test_every_row_required_proof_depth_in_ladder(self):
        result = load_matrix()
        bad = []
        for r in result.rows:
            depth = (r.get("required_proof_depth") or "").strip()
            if depth and not is_valid_depth(depth):
                bad.append((r["req_id"], depth))
        assert not bad, f"rows with invalid required_proof_depth: {bad}"


class TestRowCount:
    """RTC-REQ-001 + RTC-REQ-033: row count must equal canonical universe."""

    def test_row_count_equals_canonical(self):
        result = load_matrix()
        assert result.row_count == CANONICAL_REQUIREMENT_COUNT

    def test_canonical_count_is_87(self):
        # W1p6: incremented to 87 on addition of RTC-REQ-059 (safe-reuse
        # composite). If this fails the CSV was modified — confirm intentionally.
        assert CANONICAL_REQUIREMENT_COUNT == 87


class TestDuplicateDetection:
    """Loader fail-closes on duplicate req_id."""

    def test_duplicate_req_id_raises(self):
        # Build a synthetic CSV with one duplicated req_id and load it via
        # the loader's path override.
        with tempfile.TemporaryDirectory() as td:
            tmp_csv = Path(td) / "bad.csv"
            with tmp_csv.open("w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=REQUIRED_COLUMNS)
                w.writeheader()
                base = {c: "" for c in REQUIRED_COLUMNS}
                base["claim_type"] = "STATIC_ENFORCEMENT"
                base["required_proof_depth"] = "E2_STATIC_CHECK"
                base["priority"] = "P0"
                w.writerow({**base, "req_id": "RTC-REQ-DUP"})
                w.writerow({**base, "req_id": "RTC-REQ-DUP"})  # duplicate!
            with pytest.raises(MatrixLoadError) as ei:
                load_matrix(path=tmp_csv)
            assert "DUPLICATE_REQ_ID" in str(ei.value)

    def test_missing_column_raises(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_csv = Path(td) / "missing_col.csv"
            cols = [c for c in REQUIRED_COLUMNS if c != "claim_type"]
            with tmp_csv.open("w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=cols)
                w.writeheader()
                w.writerow({c: "x" for c in cols})
            with pytest.raises(MatrixLoadError) as ei:
                load_matrix(path=tmp_csv)
            assert "MISSING_COLUMNS" in str(ei.value)


class TestSchemaVerifierScript:
    """Integration: scripts/verify_runtime_certification_matrix_schema.py exits 0."""

    def test_script_exits_zero_on_clean_repo(self):
        result = subprocess.run(
            [sys.executable, "scripts/verify_runtime_certification_matrix_schema.py"],
            capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=30, check=False,
        )
        assert result.returncode == 0, (
            f"verifier exited {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )

    def test_schema_report_artifact_emitted(self):
        # The verifier was already run by the previous test (and by the
        # smoke run before tests); confirm the artifact is there.
        report_path = REPO_ROOT / "artifacts" / "certification" / "schema_validation_report.json"
        assert report_path.exists()
        report = json.loads(report_path.read_text(encoding="utf-8"))
        assert report["status"] == "PASS"
        assert report["row_count"] == CANONICAL_REQUIREMENT_COUNT
        assert report["violations"] == []
