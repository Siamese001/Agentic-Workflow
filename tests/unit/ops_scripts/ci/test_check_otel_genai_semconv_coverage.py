"""Tests for ops_scripts/ci/check_otel_genai_semconv_coverage.py.

Tier: unit
Plan: .windsurf/plans/three-bucket-otel-view-5db409.md (W4.P4.2)
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
GATE = REPO_ROOT / "ops_scripts" / "ci" / "check_otel_genai_semconv_coverage.py"

__adg_consumer_mode__ = "inventory"


def _run_gate(*args: str, env: dict | None = None) -> tuple[int, str]:
    cmd = [sys.executable, str(GATE), *args]
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=60,
        env=full_env,
        check=False,
    )
    return proc.returncode, proc.stdout + proc.stderr


class TestGateRunsAndProducesReport:
    """Smoke test: the gate scans the repo and emits a structured result."""

    def test_advisory_mode_default_does_not_block(self) -> None:
        # The repo currently has 0% alignment; the gate must NOT block in
        # advisory mode (default).
        rc, out = _run_gate()
        assert rc == 0
        assert "emitters=" in out
        assert "coverage=" in out
        assert "threshold=" in out

    def test_lower_threshold_to_zero_passes_strict(self) -> None:
        # With threshold=0, ANY emitter coverage passes — exit 0 even in strict.
        rc, out = _run_gate("--threshold", "0", "--strict")
        assert rc == 0


class TestGateBypass:
    def test_bypass_envvar_skips(self) -> None:
        rc, out = _run_gate("--strict", env={"GENAI_SEMCONV_BYPASS": "1"})
        assert rc == 0
        assert "bypass active" in out


class TestGateStrictMode:
    def test_strict_with_high_threshold_blocks(self) -> None:
        # Repo currently has 0% alignment; threshold 99 + strict must block.
        rc, out = _run_gate("--threshold", "99", "--strict")
        assert rc == 1
        assert "below_threshold" in out or "coverage=" in out

    def test_advisory_with_high_threshold_does_not_block(self) -> None:
        rc, _ = _run_gate("--threshold", "99")
        # Advisory: returns 0 even when below threshold.
        assert rc == 0


class TestGateReportSchema:
    """Report file has the expected keys."""

    def test_report_keys_present(self, tmp_path: Path) -> None:
        _run_gate()
        import json

        report = (
            REPO_ROOT
            / "docs"
            / "reports"
            / "adg"
            / "otel_genai_semconv_gate_report.json"
        )
        assert report.exists()
        data = json.loads(report.read_text(encoding="utf-8"))
        for key in (
            "gate",
            "tier",
            "timestamp",
            "threshold_pct",
            "files_scanned",
            "emitters_detected",
            "emitters_aligned",
            "emitters_unaligned",
            "coverage_pct",
            "status",
            "unaligned_files",
        ):
            assert key in data, f"missing key {key}"
        assert data["gate"] == "G-OTEL-GENAI-SEMCONV-COVERAGE"
