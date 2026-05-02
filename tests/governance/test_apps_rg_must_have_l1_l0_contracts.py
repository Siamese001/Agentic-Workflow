"""Test 2 — Latest apps_rg run must persist L1PlanContract + RouteContract.

Fails today: ``GovernedAppRunner.run_governed_core`` returns a Python value
record but does not call ``emit_artifact()``; no L1Plan/RouteContract files
are written to disk.

Remediation: plan ``apps-rg-governed-runtime-b8d4f1.md`` Wave 2 Phases 2.1-2.2.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.mark.governance
@pytest.mark.xfail(
    reason="Governance gap: L1PlanContract + RouteContract not persisted by R3 path. "
    "Remediation: plan apps-rg-governed-runtime-b8d4f1.md Wave 2 P2.1-2.2.",
    strict=True,
)
def test_l1_plan_and_route_contract_persisted(latest_apps_rg_run_dir: Path) -> None:
    contracts_dir = latest_apps_rg_run_dir / "contracts"
    assert contracts_dir.is_dir(), (
        f"Expected contracts/ subdir under {latest_apps_rg_run_dir} — "
        "the run must persist L1PlanContract and RouteContract artifacts."
    )

    l1 = contracts_dir / "l1_plan_contract.json"
    route = contracts_dir / "route_contract.json"
    assert l1.exists(), f"missing L1PlanContract artifact at {l1}"
    assert route.exists(), f"missing RouteContract artifact at {route}"

    l1_doc = json.loads(l1.read_text(encoding="utf-8"))
    route_doc = json.loads(route.read_text(encoding="utf-8"))

    # Schema floor — these fields are required by the audit standard.
    for field in ("request_id", "run_id", "trace_root", "task_spec", "query_spec"):
        assert field in l1_doc, f"L1PlanContract missing required field: {field}"
    for field in (
        "request_id",
        "run_id",
        "trace_root",
        "route_id",
        "execution_form",
        "grounding_required",
        "model_execution_required",
        "l3_required",
        "durable_mutation_requested",
    ):
        assert field in route_doc, f"RouteContract missing required field: {field}"

    # Cross-receipt ID join — same run.
    for field in ("request_id", "run_id", "trace_root"):
        assert l1_doc[field] == route_doc[field], (
            f"ID mismatch on {field}: L1={l1_doc[field]!r} vs Route={route_doc[field]!r}"
        )
