"""W6 + W2 contract tests for apps_rg PA boundary anti-bypass scanner.

W2 additions (ADR-083, plan apps-rg-spine-hardening-deferred-wave-2f8b1d):
- CONDITIONAL_V1_BASELINED is reported as WARN not ERROR
- agentic_core/prompt_governance/ is scanned by default
- --no-agentic-core skips the agentic_core surface
- --scan-dir limits scan to a specific directory
- ADR-083 is referenced in scanner output
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCANNER = REPO_ROOT / "ops_scripts" / "ci" / "check_apps_rg_pa_boundary.py"


def _load_scanner_source() -> str:
    """Return scanner source as a string for structural assertions."""
    return SCANNER.read_text(encoding="utf-8")


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
    """Scanner writes to artifacts/cursor/apps_rg_pa_boundary_violations.jsonl."""
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


# ── W2 tests (ADR-083) ──────────────────────────────────────────────────────


def test_conditional_v1_in_allowlist():
    """hops/_llm_client.py is in CONDITIONAL_V1_BASELINE (WARN not ERROR)."""
    src = _load_scanner_source()
    assert "apps_rg/integrations/hops/_llm_client.py" in src
    assert "CONDITIONAL_V1_BASELINE" in src


def test_agentic_core_allowlist_present():
    """ALLOWLIST_AGENTIC_CORE includes pa6_provider_rendering.py."""
    src = _load_scanner_source()
    assert "pa6_provider_rendering" in src
    assert "ALLOWLIST_AGENTIC_CORE" in src


def test_scanner_reports_conditional_v1_count():
    """Scanner output includes CONDITIONAL_V1_BASELINED count."""
    result = _run_scanner()
    assert "CONDITIONAL_V1_BASELINED=" in result.stdout


def test_scanner_no_agentic_core_flag():
    """--no-agentic-core runs advisory without scanning prompt_governance."""
    env = os.environ.copy()
    env.pop("APPS_RG_PA_BOUNDARY_FAIL_CLOSED", None)
    env.pop("APPS_RG_PA_BOUNDARY_BYPASS", None)
    result = subprocess.run(
        [sys.executable, str(SCANNER), "--quiet", "--no-agentic-core"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
    )
    assert result.returncode == 0
    assert "[apps_rg-pa-boundary] scanned" in result.stdout


def test_scanner_scan_dir_flag():
    """--scan-dir limits scan to specified directory."""
    env = os.environ.copy()
    env.pop("APPS_RG_PA_BOUNDARY_FAIL_CLOSED", None)
    env.pop("APPS_RG_PA_BOUNDARY_BYPASS", None)
    result = subprocess.run(
        [sys.executable, str(SCANNER), "--quiet", "--scan-dir", "apps_rg/cache"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
    )
    assert result.returncode == 0
    assert "[apps_rg-pa-boundary] scanned" in result.stdout


def test_adr_083_exists():
    """ADR-083 (PA ownership boundary) is committed to docs/architecture/adr/."""
    adr = REPO_ROOT / "docs" / "architecture" / "adr" / "ADR-083-apps-rg-pa-ownership-boundary.md"
    assert adr.exists(), f"ADR-083 missing at {adr}"
    content = adr.read_text(encoding="utf-8")
    assert "CONDITIONAL_V1" in content
    assert "NEXT_STEP-1" in content
    assert "ADR-083" in content


# ---------------------------------------------------------------------------
# W4 — P4.1 baseline + P4.2 calibration cadence (2026-05-09)
# ---------------------------------------------------------------------------

def test_hardened_anthropic_executor_in_allowlist():
    """HardenedanthropicexecutorStrategy (both copies) must be in ALLOWLIST_FILES — W4 P4.1."""
    src = _load_scanner_source()
    assert "apps_rg/enforcement/HardenedanthropicexecutorStrategy.py" in src
    assert "apps_rg/validators/enforcement/HardenedanthropicexecutorStrategy.py" in src


def test_v3_respects_conditional_v1_baseline():
    """V3 (raw-string LLM call) must emit CONDITIONAL_V1_BASELINED not ERROR for baselined files — W4 P4.1."""
    src = _load_scanner_source()
    assert "conditional_v3" in src, "V3 check must compute conditional_v3 flag"
    assert "CONDITIONAL_V1_BASELINED" in src


def test_v2_excludes_prompt_governance_assembly():
    """V2 path exclusion must cover agentic_core/prompt_governance/prompt_assembly — W4 P4.1."""
    src = _load_scanner_source()
    assert "prompt_governance/prompt_assembly" in src


def test_calibration_report_exists():
    """pa_boundary_weekly_report.py must exist at ops_scripts/calibration/ — W4 P4.2."""
    report = REPO_ROOT / "ops_scripts" / "calibration" / "pa_boundary_weekly_report.py"
    assert report.exists(), f"Calibration report missing at {report}"


def test_calibration_report_generates_markdown(tmp_path):
    """Calibration report generate_report() returns valid markdown — W4 P4.2."""
    sys.path.insert(0, str(REPO_ROOT))
    from ops_scripts.calibration.pa_boundary_weekly_report import generate_report
    md = generate_report(weeks=4)
    assert "# PA Boundary Weekly Calibration Report" in md
    assert "| Week |" in md
    assert "ERROR=0" in md or "Fail-closed" in md


def test_gate_label_reflects_baseline():
    """Gate label in run_contract_gates.py must reference baseline date — W4 P4.1."""
    gates_src = (REPO_ROOT / "ops_scripts" / "ci" / "run_contract_gates.py").read_text(encoding="utf-8")
    assert "baseline clean 2026-05-09" in gates_src, \
        "PA-RG1 gate label must note baseline clean date"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
