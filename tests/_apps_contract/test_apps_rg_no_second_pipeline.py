"""W1 ratchet: apps_rg must not use second pipeline in product paths (d8f4a2).

PROOF_CLASSIFICATION: CI_STATIC_CONTRACT_SCAN + negative-control synthesis only.
Does NOT claim LIVE_RUNTIME_PROOF or RELEASE_ELIGIBLE_PROOF.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCAN = REPO / "ops_scripts" / "ci" / "apps_rg_single_spine_scan.py"
GATE = REPO / "ops_scripts" / "ci" / "check_apps_rg_single_spine.py"

if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from ops_scripts.ci.apps_rg_single_spine_scan import (  # noqa: E402
    SPINE_SECTION_CONTRACT_FILENAMES,
    SingleSpineFinding,
    findings_with_errors,
    scan_file,
    scan_product_paths,
)


def test_spine_section_contract_filenames_frozen() -> None:
    """Section runs must target spine SSOT artifact names (not mirror substitutes)."""
    assert "validated_request.json" in SPINE_SECTION_CONTRACT_FILENAMES
    assert "exit_disposition_receipt.json" in SPINE_SECTION_CONTRACT_FILENAMES
    assert "final_evidence_contract.json" in SPINE_SECTION_CONTRACT_FILENAMES
    assert "x3_disposition.json" not in SPINE_SECTION_CONTRACT_FILENAMES


def test_scan_detects_synthetic_forbidden_bridge_import(tmp_path: Path) -> None:
    """Negative control: gate must catch a forbidden bridge import."""
    bad = tmp_path / "synthetic_product.py"
    bad.write_text(
        "from apps_rg.runtime.spine.c0_fec_compose import wire_spine_c0_fec_for_section\n",
        encoding="utf-8",
    )
    findings = scan_file(bad, tmp_path)
    codes = {f.code for f in findings}
    assert "FORBIDDEN_BRIDGE_IMPORT" in codes or "SUSPICIOUS_BRIDGE_IMPORT" in codes


def test_scan_detects_synthetic_lane_from_cli(tmp_path: Path) -> None:
    dispatch = tmp_path / "apps_rg/runtime/orchestration/canonical_dispatch.py"
    dispatch.parent.mkdir(parents=True, exist_ok=True)
    dispatch.write_text(
        "def _run_executive_summary_lane_from_cli():\n    return {}\n",
        encoding="utf-8",
    )
    findings = scan_file(dispatch, tmp_path)
    assert any(f.code == "FORBIDDEN_LANE_FROM_CLI" for f in findings)


def test_scan_detects_x3_without_exit_eval_pipeline(tmp_path: Path) -> None:
    lane = tmp_path / "apps_rg/runtime/sections/fake_lane.py"
    lane.parent.mkdir(parents=True, exist_ok=True)
    lane.write_text(
        "from apps_rg.runtime.exit.executive_summary_x3 import aggregate_x3\n"
        "def run():\n"
        "    x3 = aggregate_x3(resume_display_text='x', claim_ledger=[], x2_gates=[], x1d_judges=[])\n"
        "    open('x3_disposition.json', 'w').write('{}')\n",
        encoding="utf-8",
    )
    findings = scan_file(lane, tmp_path)
    codes = {f.code for f in findings}
    assert "X3_WITHOUT_SPINE_EXIT_RECEIPT" in codes
    assert "LANE_AGGREGATE_X3_AS_AUTHORITY" in codes


def test_product_paths_pass_single_spine_gate_when_clean() -> None:
    """Product paths must have zero single-spine ERROR findings (d8f4a2 W2+)."""
    errors = findings_with_errors(scan_product_paths(REPO))
    assert not errors, f"single-spine violations: {errors[:5]}"


def test_ci_gate_script_exits_zero_when_clean() -> None:
    """Gate must pass when second pipeline is removed."""
    import os

    env = dict(os.environ)
    env["APPS_RG_SINGLE_SPINE_GATE_BYPASS"] = "0"
    env.pop("APPS_RG_SINGLE_SPINE_GATE_ADVISORY", None)
    completed = subprocess.run(
        [sys.executable, str(GATE)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
        env=env,
    )
    assert completed.returncode == 0, (
        f"Expected zero exit when product paths are clean; "
        f"stdout={completed.stdout[-800:]!r} stderr={completed.stderr[-800:]!r}"
    )


def test_ci_gate_report_json_written() -> None:
    report = REPO / "artifacts" / "ci" / "apps_rg_single_spine_gate.json"
    subprocess.run(
        [sys.executable, str(GATE), "--report-only"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert report.is_file()
    data = json.loads(report.read_text(encoding="utf-8"))
    assert data.get("plan_id") == "apps-rg-spine-only-unification-d8f4a2"
    assert data.get("wave") == "W1"
    assert data.get("proof_classification") == "CI_STATIC_CONTRACT_SCAN"
