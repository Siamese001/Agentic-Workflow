"""Contract checks for the apps_rg prompt/judge sync CI gate."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _read(rel_path: str) -> str:
    return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def test_sync_gate_script_runs_expected_focused_suite() -> None:
    src = _read("ops_scripts/ci/check_apps_rg_prompt_judge_sync.py")
    expected = (
        "tests/unit/apps_rg/test_section_prompt_judge_lockstep.py",
        "tests/unit/apps_rg/test_section_prompt_product_shape_drift.py",
        "tests/_apps_contract/test_section_x2_x1d_drift_ci.py",
        "tests/_apps_contract/test_apps_rg_x2_x1d_alignment.py",
        "tests/_apps_contract/test_x1d_judge_transport_parity_contract.py",
        "tests/unit/apps_rg/test_x1d_provider_transport_parity.py",
    )
    for path in expected:
        assert path in src
    assert "APPS_RG_PROMPT_JUDGE_SYNC_BYPASS" in src
    assert "timeout=TIMEOUT_SECONDS" in src


def test_sync_gate_registered_in_contract_runner() -> None:
    src = _read("ops_scripts/ci/run_contract_gates.py")
    assert "APPS-RG-PROMPT-JUDGE-SYNC" in src
    assert "check_apps_rg_prompt_judge_sync.py" in src


def test_contract_workflow_routes_prompt_sensitive_paths() -> None:
    src = _read(".github/workflows/contract-gates.yml")
    assert "apps-rg-prompt-judge-sync" in src
    for prefix in (
        "apps_rg/prompt_assembly/",
        "apps_rg/runtime/sections/",
        "apps_rg/runtime/validators/",
        "apps_rg/runtime/judges/",
        "artifacts/apps_rg/prompt_authority/",
    ):
        assert prefix in src
    assert "python ops_scripts/ci/check_apps_rg_prompt_judge_sync.py" in src
