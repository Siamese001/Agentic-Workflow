"""p3.2 DoD-4/5 — typed RouteGateReceipts on clean dry-run."""
from __future__ import annotations

from apps_rg.runtime.dispatch.apps_rg_dispatch import apps_rg_parse
from apps_rg.runtime.bindings.l1_binding import l1_plan_apps_rg
from apps_rg.runtime.bindings.u0_binding import u0_validate_apps_rg
from agentic_core.runtime.contracts.route_gate_receipt import RouteGateReceipt
from apps_rg.runtime.bindings.l0_binding import l0_route_apps_rg


def _thin() -> dict:
    return {
        "app_id": "apps_rg",
        "task_class": "resume_generation",
        "target_company": "Acme Corp",
        "target_role": "Director",
        "target_level": "STAFF",
        "source_resume_text": "Resume body.",
        "job_description_text": "JD body.",
        "manual_brief_path": "brief.md",
    }


def test_gate_receipts_are_typed_and_g07_passes_with_hashes() -> None:
    env = apps_rg_parse(_thin())
    assert env is not None
    vr = u0_validate_apps_rg(env)
    plan = l1_plan_apps_rg(vr)
    route = l0_route_apps_rg(plan)
    assert route.route_gate_receipts, "expected typed gate receipts"
    for r in route.route_gate_receipts:
        assert isinstance(r, RouteGateReceipt)
    g07 = next(r for r in route.route_gate_receipts if r.gate_id == "G07_GROUNDING_READINESS")
    assert g07.verdict == "PASS"
    g20 = next(r for r in route.route_gate_receipts if r.gate_id == "G20_ROUTE_BUDGET")
    assert g20.verdict == "UNKNOWN"
