"""W4 of plan apps-fort-knox-parity-c5d9a3 \u2014 mutation driver tests.

Covers tools/cert/apps_e2e/apps_mutation_driver.py.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.cert.apps_e2e import apps_mutation_driver as driver

REPO_ROOT = Path(__file__).resolve().parents[3]


# ----------------------------- structural -----------------------------

def test_mutation_function_count():
    """At least 11 distinct tamper classes are exercised (W4 SCC: \u226511)."""
    assert len(driver._MUTATION_FUNCS) >= 11


def test_mutation_function_names_are_unique():
    names = [fn.__name__ for fn in driver._MUTATION_FUNCS]
    assert len(set(names)) == len(names)


# ----------------------------- end-to-end -----------------------------

@pytest.fixture
def synthetic_workspace(tmp_path, monkeypatch):
    """Materialize a tiny apps_e2e/ tree under tmp_path so mutations have
    real artifacts to clone without touching the live repo state."""
    apps_dir = tmp_path / "apps_e2e"
    apps_dir.mkdir(parents=True)
    sandbox = apps_dir / "_mutation_sandbox"

    verifier_report = {
        "exit_code": 0,
        "generated_at_utc": "2026-05-02T12:00:00+00:00",
        "mode": "strict",
        "rows": [
            {
                "app_name": "apps_eval", "bundle_present": True,
                "certification_level": "SPINE_COMPLETE_CERTIFIED",
                "mode": "strict", "violation_count": 0, "violations": [],
            },
        ],
        "summary": {"n_apps": 1, "n_pass": 1, "n_fail": 0},
        "verifier_report_schema_version": "apps_e2e_verifier_report/2026-05-02/v1",
    }
    matrix = {
        "apps": [{"app_name": "apps_eval", "certification_level": "SPINE_COMPLETE_CERTIFIED"}],
        "schema_version": "apps_e2e_matrix/2026-05-02/v1",
    }
    bundle = {
        "app_name": "apps_eval",
        "certification_level": "SPINE_COMPLETE_CERTIFIED",
        "synthetic_trace_detected": False,
        "mock_mode_detected": False,
        "fixture_runtime_mode": False,
    }

    (apps_dir / "verifier_report.json").write_text(
        json.dumps(verifier_report, sort_keys=True), encoding="utf-8"
    )
    (apps_dir / "apps_e2e_matrix.json").write_text(
        json.dumps(matrix, sort_keys=True), encoding="utf-8"
    )
    (apps_dir / "apps_eval").mkdir()
    (apps_dir / "apps_eval" / "apps_eval_e2e_proof.json").write_text(
        json.dumps(bundle, sort_keys=True), encoding="utf-8"
    )

    monkeypatch.setattr(driver, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(driver, "APPS_E2E_DIR", apps_dir)
    monkeypatch.setattr(driver, "SANDBOX_DIR", sandbox)
    monkeypatch.setattr(driver, "REPORT_PATH", apps_dir / "apps_mutation_rejection_report.json")
    return tmp_path


def test_run_mutations_produces_scenarios(synthetic_workspace):
    scenarios = driver.run_mutations()
    assert len(scenarios) >= 11  # at least one mutation per class


def test_all_in_scope_scenarios_are_rejected(synthetic_workspace):
    scenarios = driver.run_mutations()
    in_scope = [s for s in scenarios if "not applicable" not in (s["compiler_reason"] or "")]
    rejected = [s for s in in_scope if s["passes_rejection"]]
    accepted = [s for s in in_scope if not s["passes_rejection"]]
    assert not accepted, "compiler validator accepted a tampered scenario: " + ", ".join(
        f"{s['name']}: {s['compiler_reason']}" for s in accepted
    )
    assert rejected, "no scenarios were rejected; driver may be broken"


def test_report_summary_counts_match(synthetic_workspace):
    scenarios = driver.run_mutations()
    report = driver.build_report(scenarios)
    s = report["summary"]
    assert s["total"] == len(scenarios)
    assert s["accepted"] == 0
    assert s["rejected"] >= 1
    assert "rejection_rate" in s
    assert s["rejection_rate"] == 1.0  # 100% of in-scope rejected


def test_report_has_by_tamper_class_index(synthetic_workspace):
    scenarios = driver.run_mutations()
    report = driver.build_report(scenarios)
    assert "by_tamper_class" in report
    assert len(report["by_tamper_class"]) >= 8  # most classes apply


def test_report_has_per_app_index(synthetic_workspace):
    scenarios = driver.run_mutations()
    report = driver.build_report(scenarios)
    assert "scenarios_by_app" in report
    # Synthetic workspace has only apps_eval
    assert "apps_eval" in report["scenarios_by_app"]


def test_main_writes_report_and_returns_zero(synthetic_workspace, capsys):
    out = synthetic_workspace / "apps_e2e" / "apps_mutation_rejection_report.json"
    rc = driver.main(["--out", str(out), "--quiet"])
    assert rc == 0
    assert out.exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["summary"]["accepted"] == 0


def test_sandbox_resets_between_runs(synthetic_workspace):
    """Running twice should not leave stale clones from a previous run."""
    driver.run_mutations()
    first_files = set(p.name for p in driver.SANDBOX_DIR.iterdir())
    driver.run_mutations()
    second_files = set(p.name for p in driver.SANDBOX_DIR.iterdir())
    # Same set (deterministic clones each run)
    assert first_files == second_files


# ----------------------------- live smoke -----------------------------

@pytest.mark.skipif(
    not (REPO_ROOT / "artifacts" / "certification" / "apps_e2e" / "verifier_report.json").exists(),
    reason="live verifier_report.json not present",
)
def test_live_driver_rejects_all_in_scope_scenarios():
    """Live run against real production artifacts."""
    scenarios = driver.run_mutations()
    in_scope = [s for s in scenarios if "not applicable" not in (s["compiler_reason"] or "")]
    accepted = [s for s in in_scope if not s["passes_rejection"]]
    # Hostile-reviewer SCC: zero accepts
    assert not accepted, (
        "live driver accepted tampered scenario(s): "
        + ", ".join(f"{s['name']}: {s['compiler_reason']}" for s in accepted)
    )
    assert len(in_scope) >= 30, f"expected \u2265 30 in-scope scenarios; got {len(in_scope)}"
