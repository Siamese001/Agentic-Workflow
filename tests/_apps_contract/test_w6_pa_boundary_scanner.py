"""W6 contract tests for apps_rg PA boundary anti-bypass scanner."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCANNER = REPO_ROOT / "ops_scripts" / "ci" / "check_apps_rg_pa_boundary.py"


def _run_scanner(env_overrides: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env.pop("APPS_RG_PA_BOUNDARY_FAIL_CLOSED", None)
    env.pop("APPS_RG_PA_BOUNDARY_BYPASS", None)
    if env_overrides:
        env.update(env_overrides)
    return subprocess.run(
        [sys.executable, str(SCANNER), "--quiet"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
    )


def test_scanner_exists():
    assert SCANNER.exists(), f"Scanner missing at {SCANNER}"


def test_scanner_runs_advisory_default_exits_zero():
    """Advisory mode = exit 0 even with findings."""
    result = _run_scanner()
    assert result.returncode == 0
    assert "[apps_rg-pa-boundary] scanned" in result.stdout
    assert "mode=advisory" in result.stdout


def test_scanner_emits_finding_counts():
    """Output includes ERROR/WARN counts."""
    result = _run_scanner()
    assert "ERROR=" in result.stdout
    assert "WARN=" in result.stdout


def test_scanner_bypass_env_var():
    """APPS_RG_PA_BOUNDARY_BYPASS=1 short-circuits scanner."""
    result = _run_scanner({"APPS_RG_PA_BOUNDARY_BYPASS": "1"})
    assert result.returncode == 0
    assert "BYPASSED" in result.stdout


def test_scanner_fail_closed_returns_nonzero_when_errors_present():
    """APPS_RG_PA_BOUNDARY_FAIL_CLOSED=1 returns nonzero if ERROR findings exist."""
    result = _run_scanner({"APPS_RG_PA_BOUNDARY_FAIL_CLOSED": "1"})
    # First-run baseline expected to have ERROR findings
    if "ERROR=0" not in result.stdout:
        assert result.returncode == 1
    else:
        assert result.returncode == 0


def test_scanner_writes_violations_log():
    """Scanner writes to artifacts/windsurf/apps_rg_pa_boundary_violations.jsonl."""
    log_path = REPO_ROOT / "artifacts" / "windsurf" / "apps_rg_pa_boundary_violations.jsonl"
    initial_size = log_path.stat().st_size if log_path.exists() else 0
    _run_scanner()
    assert log_path.exists()
    assert log_path.stat().st_size > initial_size


def test_scanner_registered_in_run_contract_gates():
    """PA-RG1 gate is registered in run_contract_gates.py."""
    rcg = REPO_ROOT / "ops_scripts" / "ci" / "run_contract_gates.py"
    content = rcg.read_text(encoding="utf-8")
    assert "PA-RG1" in content
    assert "check_apps_rg_pa_boundary.py" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
