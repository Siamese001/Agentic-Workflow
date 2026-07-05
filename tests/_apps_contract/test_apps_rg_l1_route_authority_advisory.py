"""apps-test-model: APP CONTRACT.

L1 route_hints are ADVISORY_ONLY; L0 RouteContract is route authority.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from datetime import datetime, timezone

from agentic_core.L0_routing.u0_intake_validator import AuthorityValidationReceipt
from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from apps_rg.runtime.bindings.l1_binding import l1_plan_apps_rg

REPO = Path(__file__).resolve().parents[2]
APPS_RG_RUNTIME = REPO / "apps_rg" / "runtime"

_ROUTE_AUTHORITY_ACCESSORS = (
    "route_hints",
    "plan.route_hints",
    "l1_plan.route_hints",
)


def _minimal_validated_request(*, generation_mode: str = "strategic_tailor") -> object:
    from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest

    return ValidatedRequest(
        request_id="req-l1-auth",
        run_id="run-l1-auth",
        app_id="apps_rg",
        trace_id="trace-l1-auth",
        task_class="resume_generation",
        payload_digest="a" * 64,
        authority_validation_receipt=AuthorityValidationReceipt(
            validation_timestamp=datetime.now(timezone.utc).isoformat(),
        ),
        l5_certification_ref="test:valid:w6",
        app_payload={
            "non_product_certified": True,
            "target_company": "Acme",
            "target_role": "VP Engineering",
            "task_spec": {"generation_mode": generation_mode},
            "query_spec": {"target_level": "VP"},
            "support_expectation": {},
            "output_expectation": {},
        },
    )


def test_l1_route_hints_marked_advisory_only() -> None:
    plan = l1_plan_apps_rg(_minimal_validated_request())
    assert plan.route_hints.get("authority_class") == "ADVISORY_ONLY"


def test_l1_plan_contract_rejects_route_authority_keys_in_hints() -> None:
    from dataclasses import replace

    plan = l1_plan_apps_rg(_minimal_validated_request())
    bad_hints = dict(plan.route_hints)
    bad_hints["route_id"] = "R4_MANAGED_DRAFT"
    with pytest.raises(ValueError, match="forbidden route-authority key"):
        replace(plan, route_hints=bad_hints)


def test_apps_rg_runtime_does_not_use_route_hints_for_routing() -> None:
    """No gate/lane/runtime module may read L1 route_hints as executable route selection."""
    violations: list[str] = []
    for path in APPS_RG_RUNTIME.rglob("*.py"):
        if "bindings" in path.parts and path.name == "l1_binding.py":
            continue
        src = path.read_text(encoding="utf-8", errors="replace")
        if "route_hints" not in src:
            continue
        tree = ast.parse(src, filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                if node.attr == "route_hints" and node.value.id in {
                    "plan",
                    "l1_plan",
                    "l1",
                }:
                    rel = path.relative_to(REPO).as_posix()
                    violations.append(f"{rel}: attribute access plan.route_hints")
            if isinstance(node, ast.Subscript):
                if isinstance(node.value, ast.Name) and node.value.id == "route_hints":
                    rel = path.relative_to(REPO).as_posix()
                    violations.append(f"{rel}: subscript route_hints[...]")
    assert not violations, "route_hints used outside L1 binding:\n" + "\n".join(violations)


def test_l0_route_contract_remains_separate_from_l1_plan() -> None:
    import dataclasses

    l1_fields = {f.name for f in dataclasses.fields(L1PlanContract)}
    assert "route_id" not in l1_fields
    assert "route_family" not in l1_fields
