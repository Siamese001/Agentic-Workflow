"""p3.2 DoD-2/3 — canonical spine fields on RouteContract for full resume."""
from __future__ import annotations

from apps_rg.runtime.dispatch.apps_rg_dispatch import apps_rg_parse
from apps_rg.runtime.bindings.l1_binding import l1_plan_apps_rg
from apps_rg.runtime.bindings.u0_binding import u0_validate_apps_rg
from apps_rg.runtime.bindings.l0_binding import l0_route_apps_rg


def _thin() -> dict:
    return {
        "app_id": "apps_rg",
        "task_class": "resume_generation",
        "target_company": "Acme Corp",
        "target_role": "Senior Director of AI Engineering",
        "target_level": "EXECUTIVE",
        "source_resume_text": "Resume body.",
        "job_description_text": "JD body.",
    }


def test_full_resume_managed_workflow_spine() -> None:
    env = apps_rg_parse(_thin())
    assert env is not None
    vr = u0_validate_apps_rg(env)
    plan = l1_plan_apps_rg(vr)
    route = l0_route_apps_rg(plan)
    assert route.route_family == "R3R4_MANAGED_WORKFLOW"
    assert route.execution_form == "MANAGED_WORKFLOW"
    assert "L3" in route.allowed_next_stage
    assert route.grounding_required is True
