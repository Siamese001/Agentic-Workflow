"""Test 8 — Latest apps_rg run must produce a no-bypass assertion artifact.

Fails today: no-bypass enforcement exists only as test-harness assertions
and as a ``REQ-L6-OBS-ANTI-BYPASS-001`` telemetry claim in the REQ ledger —
neither of which is a runtime-emitted assertion artifact for the run.

Remediation: plan ``apps-rg-governed-runtime-b8d4f1.md`` Wave 5 P5.2.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest


REQUIRED_CHECKS = {
    "no_direct_l4_write",
    "no_final_output_before_exit",
    "no_direct_model_call_outside_path",
    "no_na_without_route_contract",
    "no_missing_x3",
    "no_replay_noop_in_production",
}


@pytest.mark.governance
@pytest.mark.xfail(
    reason="Governance gap: no production no-bypass-assertion writer exists "
    "(only test-harness + REQ-L6-OBS-ANTI-BYPASS-001 telemetry claim). "
    "Remediation: plan apps-rg-governed-runtime-b8d4f1.md Wave 5 P5.2.",
    strict=True,
)
def test_no_bypass_assertion_artifact_present(latest_apps_rg_run_dir: Path) -> None:
    nb_dir = latest_apps_rg_run_dir / "no_bypass"
    receipt = nb_dir / "no_bypass_assertion_receipt.json"
    assert receipt.exists(), (
        f"missing no-bypass assertion artifact at {receipt} — telemetry claims do not satisfy this"
    )

    doc = json.loads(receipt.read_text(encoding="utf-8"))
    for field in ("request_id", "run_id", "trace_root", "checks", "all_passed"):
        assert field in doc, f"no-bypass receipt missing required field: {field}"

    checks = doc["checks"]
    assert isinstance(checks, dict), "checks field must be dict mapping check_id -> verdict"
    for required in REQUIRED_CHECKS:
        assert required in checks, f"no-bypass receipt missing required check: {required}"
        assert checks[required] in ("pass", "fail"), (
            f"check {required!r} verdict must be 'pass' or 'fail', got {checks[required]!r}"
        )

    assert doc["all_passed"] is True, (
        f"no-bypass assertion failed: {[k for k, v in checks.items() if v != 'pass']}"
    )
