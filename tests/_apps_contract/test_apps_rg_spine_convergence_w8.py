"""W8 — apps_rg spine convergence contract (span checklist + gap audit + CI gate)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]


@pytest.mark.apps_contract
def test_apps_rg_spine_span_checklist_has_eight_layers() -> None:
    from system_learning.runtime_adg.span_contracts import (
        APPS_RG_SPINE_SPAN_CHECKLIST,
        apps_rg_spine_span_checklist_report,
    )

    assert len(APPS_RG_SPINE_SPAN_CHECKLIST) == 8
    report = apps_rg_spine_span_checklist_report()
    assert report["row_count"] == 8
    keys = {r.layer_key for r in APPS_RG_SPINE_SPAN_CHECKLIST}
    assert keys == {"U0", "L1", "L0", "C0", "PA", "L2", "EXIT", "L6"}


@pytest.mark.apps_contract
def test_apps_rg_spine_req_gap_audit_p0_open_zero() -> None:
    script = REPO / "ops_scripts" / "apps_rg" / "apps_rg_spine_req_gap_audit.py"
    completed = subprocess.run(
        [sys.executable, str(script)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    audit_path = REPO / "artifacts" / "apps_rg" / "plans" / "apps_rg_spine_req_gap_audit.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    assert audit["p0_count"] == 0
    assert audit["convergence_status"] == "PASS"
    assert "W8" in audit["waves_completed"]


@pytest.mark.apps_contract
def test_apps_rg_spine_convergence_w8_gate_passes() -> None:
    gate = REPO / "ops_scripts" / "ci" / "check_apps_rg_spine_convergence_w8.py"
    env = {**__import__("os").environ}
    env.pop("APPS_RG_SPINE_CONVERGENCE_BYPASS", None)
    env.pop("APPS_RG_SINGLE_SPINE_GATE_BYPASS", None)
    completed = subprocess.run(
        [sys.executable, str(gate)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
        env=env,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report_path = REPO / "artifacts" / "ci" / "apps_rg_spine_convergence_w8_gate.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
