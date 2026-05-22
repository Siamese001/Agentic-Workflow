"""p3.2 DoD-7 — personalization disables R1A/R1B for default full-resume profile."""
from __future__ import annotations

from apps_rg.runtime.dispatch.apps_rg_dispatch import apps_rg_parse
from apps_rg.runtime.bindings.l1_binding import l1_plan_apps_rg
from apps_rg.runtime.bindings.u0_binding import u0_validate_apps_rg
from apps_rg.runtime.bindings.l0_binding import l0_route_apps_rg


def test_personalization_disables_exact_and_semantic_cache() -> None:
    env = apps_rg_parse(
        {
            "app_id": "apps_rg",
            "task_class": "resume_generation",
            "target_company": "Co",
            "target_role": "Role",
            "target_level": "STAFF",
            "source_resume_text": "R",
            "job_description_text": "J",
        }
    )
    assert env is not None
    vr = u0_validate_apps_rg(env)
    plan = l1_plan_apps_rg(vr)
    route = l0_route_apps_rg(plan)
    assert route.personalization_required is True
    ce = dict(route.cache_eligibility)
    assert ce["r1a_exact"] is False
    assert ce["r1b_semantic"] is False
