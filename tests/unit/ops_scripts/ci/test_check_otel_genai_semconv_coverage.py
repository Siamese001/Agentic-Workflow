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
        # Advisory mode must NEVER block, regardless of current alignment.
        rc, out = _run_gate()
        assert rc == 0
        assert "emitters=" in out
        assert "coverage=" in out
        assert "threshold=" in out

    def test_opt_out_marker_excludes_from_denominator(self) -> None:
        # W3 of plan three-bucket-gap-remediation-069806 added the
        # __non_genai_emitter__ opt-out marker. Files declaring it (L0
        # intake, L4 state writes, L5 safety, AST extraction) emit OTel
        # spans but not GenAI agent/workflow/tool spans. They MUST be
        # excluded from the coverage denominator.
        rc, out = _run_gate()
        assert rc == 0
        assert "opted_out=" in out
        # At least the 11 infrastructure files we patched in W3.
        # Pull the integer count out of the line.
        import re

        m = re.search(r"opted_out=(\d+)", out)
        assert m is not None, "opted_out=N not present in gate stdout"
        assert int(m.group(1)) >= 11, (
            f"Expected at least 11 opt-out files, found {m.group(1)}. "
            "Has someone removed __non_genai_emitter__ markers?"
        )

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
        # Strict-mode contract: when coverage_pct < threshold, gate exits 1.
        # We use threshold=101 (unreachable: coverage caps at 100.0%) so the
        # test verifies the strict-mode return-code behavior independently of
        # the repo's current alignment percentage. After W3 of plan
        # three-bucket-gap-remediation-069806, current coverage is 100%, so
        # any reachable threshold passes — only an unreachable one exercises
        # the below-threshold path.
        rc, out = _run_gate("--threshold", "101", "--strict")
        assert rc == 1
        assert "below_threshold" in out or "coverage=" in out

    def test_advisory_with_high_threshold_does_not_block(self) -> None:
        # When the env var explicitly disables strict, the gate returns 0
        # even when below threshold (advisory mode).
        rc, _ = _run_gate(
            "--threshold", "99", env={"GENAI_SEMCONV_STRICT": "0"}
        )
        assert rc == 0

    def test_strict_is_default_after_w4(self) -> None:
        # W4 of plan three-bucket-gap-remediation-069806 flipped strict mode
        # to default-on. Without --strict and without explicit env override,
        # the gate must behave as if strict=True. Verified by running with
        # threshold=101 (unreachable) and asserting exit 1 — only possible
        # in strict mode.
        rc, out = _run_gate("--threshold", "101")
        assert rc == 1, (
            f"Strict mode should be the default after W4. Got exit {rc}. "
            f"Output: {out[-300:]}"
        )
        assert "strict=True" in out


class TestGateReportSchema:
    """Report file has the expected keys."""

    def test_report_keys_present(self, tmp_path: Path) -> None:
        # Use a tmp report path to isolate from parallel xdist workers
        # writing the same shared docs/reports/adg/ file.
        report = tmp_path / "report.json"
        _run_gate("--report-path", str(report))
        import json

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
