"""Tests — Source divergence (RTC-REQ-032).

Plan: ``.windsurf/plans/runtime-cert-hardened-w0-7e3c9a.md``

Coverage
--------

  - Single-baseline behaviour passes
  - Two verifier reports with differing row_count triggers SOURCE_DIVERGENCE
  - A peer report with row_count=0 forces SOURCE_DIVERGENCE
  - A peer report with mismatched csv_sha256 forces SOURCE_DIVERGENCE
  - Source-divergence report artifact is well-formed
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "certification"


def _run_verifier() -> int:
    return subprocess.run(
        [sys.executable, "scripts/verify_source_divergence.py"],
        capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=30, check=False,
    ).returncode


def _backup_artifacts() -> dict[str, str]:
    backups = {}
    for name in (
        "canonical_universe_manifest.json",
        "requirement_count_receipt.json",
        "schema_validation_report.json",
        "acceptance_legality_report.json",
    ):
        p = ARTIFACTS_DIR / name
        if p.exists():
            backups[name] = p.read_text(encoding="utf-8")
    return backups


def _restore_artifacts(backups: dict[str, str]) -> None:
    for name, content in backups.items():
        (ARTIFACTS_DIR / name).write_text(content, encoding="utf-8")


def _ensure_baseline():
    """Run the matrix + schema + acceptance verifiers so the divergence
    verifier has peer reports to inspect."""
    for s in (
        "verify_runtime_certification_matrix",
        "verify_runtime_certification_matrix_schema",
        "verify_runtime_certification_acceptance",
    ):
        subprocess.run(
            [sys.executable, f"scripts/{s}.py"],
            capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=30, check=False,
        )


class TestBaselinePass:
    def test_baseline_pass_when_all_peers_agree(self):
        _ensure_baseline()
        rc = _run_verifier()
        assert rc == 0
        report = json.loads((ARTIFACTS_DIR / "source_divergence_report.json").read_text(encoding="utf-8"))
        assert report["status"] == "PASS"
        assert report["divergences"] == []
        assert report["baseline_count"] == 87  # W1p6: +RTC-REQ-059


class TestRowCountMismatch:
    def test_peer_with_wrong_count_triggers_divergence(self):
        _ensure_baseline()
        backups = _backup_artifacts()
        try:
            # Tamper with one peer report's row_count
            target = ARTIFACTS_DIR / "schema_validation_report.json"
            data = json.loads(target.read_text(encoding="utf-8"))
            data["row_count"] = 42  # bogus
            target.write_text(json.dumps(data), encoding="utf-8")
            rc = _run_verifier()
            assert rc == 2, "tampered peer count must trigger SOURCE_DIVERGENCE"
            report = json.loads((ARTIFACTS_DIR / "source_divergence_report.json").read_text(encoding="utf-8"))
            assert report["status"] == "FAIL_CLOSED"
            assert report["expected_fail_reason"] == "SOURCE_DIVERGENCE"
            kinds = [d["kind"] for d in report["divergences"]]
            assert "ROW_COUNT_MISMATCH" in kinds
        finally:
            _restore_artifacts(backups)


class TestPeerCountZero:
    def test_peer_with_zero_count_triggers_divergence(self):
        _ensure_baseline()
        backups = _backup_artifacts()
        try:
            target = ARTIFACTS_DIR / "acceptance_legality_report.json"
            data = json.loads(target.read_text(encoding="utf-8"))
            data["row_count"] = 0
            target.write_text(json.dumps(data), encoding="utf-8")
            rc = _run_verifier()
            assert rc == 2, "peer with row_count=0 must trigger SOURCE_DIVERGENCE per rule §7"
            report = json.loads((ARTIFACTS_DIR / "source_divergence_report.json").read_text(encoding="utf-8"))
            assert report["expected_fail_reason"] == "SOURCE_DIVERGENCE"
            assert any(d["kind"] == "ROW_COUNT_MISMATCH" and d["peer_count"] == 0
                       for d in report["divergences"])
        finally:
            _restore_artifacts(backups)


class TestSha256Mismatch:
    def test_peer_with_wrong_csv_hash_triggers_divergence(self):
        _ensure_baseline()
        backups = _backup_artifacts()
        try:
            target = ARTIFACTS_DIR / "canonical_universe_manifest.json"
            data = json.loads(target.read_text(encoding="utf-8"))
            data["csv_sha256"] = "0" * 64
            target.write_text(json.dumps(data), encoding="utf-8")
            rc = _run_verifier()
            assert rc == 2
            report = json.loads((ARTIFACTS_DIR / "source_divergence_report.json").read_text(encoding="utf-8"))
            kinds = [d["kind"] for d in report["divergences"]]
            assert "CSV_SHA256_MISMATCH" in kinds
        finally:
            _restore_artifacts(backups)


class TestReportShape:
    def test_report_has_required_fields(self):
        _ensure_baseline()
        _run_verifier()
        report = json.loads((ARTIFACTS_DIR / "source_divergence_report.json").read_text(encoding="utf-8"))
        for k in ("verifier", "executed_at_utc", "rule", "status",
                  "expected_fail_reason", "actual_fail_reason",
                  "baseline_count", "baseline_csv_sha256",
                  "canonical_count", "peers", "divergences"):
            assert k in report, f"missing field: {k}"
