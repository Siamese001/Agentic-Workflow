"""
Wave 8.1 — Tests for the L0 thin router (l0_execute.py).

Verifies:
1. run_pipeline returns correct structure in each mode
2. Scan mode produces guardian_result but no heal_result
3. Dry-run mode produces both guardian_result and heal_result
4. CLI exits cleanly in scan and dry-run modes
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

pytestmark = pytest.mark.ssot_equivalence

FIXED_UTC = "2000-01-01T00:00:00Z"

_SUBPROCESS_RETRIES = 3


def _robust_subprocess_run(
    cmd: list[str],
    **kwargs: object,
) -> subprocess.CompletedProcess[str]:
    """§Wave5.0.5: Retry on transient WinError 2 (FileNotFoundError)."""
    last_exc: FileNotFoundError | None = None
    for _ in range(_SUBPROCESS_RETRIES):
        try:
            return subprocess.run(cmd, **kwargs)  # type: ignore[arg-type]
        except FileNotFoundError as exc:
            last_exc = exc
    raise last_exc  # type: ignore[misc]


@pytest.fixture(autouse=True)
def _ensure_test_signing(monkeypatch: pytest.MonkeyPatch) -> None:
    """§Wave5.0.5: Ensure V15_TEST_SIGNING=1 for in-process guardian calls."""
    monkeypatch.setenv("V15_TEST_SIGNING", "1")


# ---------------------------------------------------------------------------
# 1. run_pipeline API tests
# ---------------------------------------------------------------------------


class TestRunPipelineAPI:
    """Test the run_pipeline function directly."""

    def test_scan_mode_returns_guardian_result(self) -> None:
        from agentic_core.L0_maintenance.scripts.l0_execute import run_pipeline

        result = run_pipeline(mode="scan", timestamp=FIXED_UTC)
        assert result["tool_id"] == "l0_execute"
        assert result["mode"] == "scan"
        assert "guardian_result" in result
        assert "heal_result" not in result

    def test_scan_mode_guardian_has_checks(self) -> None:
        from agentic_core.L0_maintenance.scripts.l0_execute import run_pipeline

        result = run_pipeline(mode="scan", timestamp=FIXED_UTC)
        guardian = result["guardian_result"]
        assert "checks" in guardian
        assert isinstance(guardian["checks"], list)
        assert len(guardian["checks"]) > 0

    def test_dry_run_mode_returns_heal_result(self, tmp_path: Path) -> None:
        from agentic_core.L0_maintenance.scripts.l0_execute import run_pipeline

        result = run_pipeline(
            mode="dry-run",
            timestamp=FIXED_UTC,
            write_artifacts_dir=str(tmp_path / "artifacts"),
        )
        assert result["mode"] == "dry-run"
        assert "guardian_result" in result
        assert "heal_result" in result

    def test_dry_run_heal_result_has_results(self, tmp_path: Path) -> None:
        from agentic_core.L0_maintenance.scripts.l0_execute import run_pipeline

        result = run_pipeline(
            mode="dry-run",
            timestamp=FIXED_UTC,
            write_artifacts_dir=str(tmp_path / "artifacts"),
        )
        heal = result["heal_result"]
        assert "results" in heal
        assert isinstance(heal["results"], list)
        assert len(heal["results"]) > 0

    def test_dry_run_all_healers_skipped(self, tmp_path: Path) -> None:
        from agentic_core.L0_maintenance.scripts.l0_execute import run_pipeline

        result = run_pipeline(
            mode="dry-run",
            timestamp=FIXED_UTC,
            write_artifacts_dir=str(tmp_path / "artifacts"),
        )
        for hr in result["heal_result"]["results"]:
            assert hr["status"] == "SKIPPED", f"{hr['check_id']} status={hr['status']}"

    def test_timestamp_injected(self) -> None:
        from agentic_core.L0_maintenance.scripts.l0_execute import run_pipeline

        result = run_pipeline(mode="scan", timestamp=FIXED_UTC)
        assert result["timestamp"] == FIXED_UTC


# ---------------------------------------------------------------------------
# 2. CLI integration tests
# ---------------------------------------------------------------------------


class TestCLI:
    """Test the CLI entry point via subprocess."""

    def test_scan_cli_exits_cleanly(self) -> None:
        result = _robust_subprocess_run(
            [
                sys.executable,
                "-m",
                "agentic_core.L0_maintenance.scripts.l0_execute",
                "--scan",
                "--format",
                "json",
                "--timestamp",
                FIXED_UTC,
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=120,
            env={**os.environ, "V15_TEST_SIGNING": "1"},
        )
        # Exit code 0 or 1 (FAIL status) are both acceptable
        assert result.returncode in (0, 1), (
            f"Unexpected exit code: {result.returncode}\nstderr: {result.stderr[:500]}"
        )
        data = json.loads(result.stdout)
        assert data["mode"] == "scan"

    def test_summary_format(self) -> None:
        result = _robust_subprocess_run(
            [
                sys.executable,
                "-m",
                "agentic_core.L0_maintenance.scripts.l0_execute",
                "--scan",
                "--format",
                "summary",
                "--timestamp",
                FIXED_UTC,
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=120,
            env={**os.environ, "V15_TEST_SIGNING": "1"},
        )
        assert result.returncode in (0, 1)
        assert "L0 Pipeline" in result.stdout
        assert "Mode: scan" in result.stdout
