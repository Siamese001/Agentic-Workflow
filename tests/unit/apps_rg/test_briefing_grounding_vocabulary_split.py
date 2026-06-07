"""apps_rg L1 vocabulary: grounding on; apps_research delegation disabled."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from agentic_core.L0_routing.u0_intake_validator import AuthorityValidationReceipt
from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest

from apps_rg.runtime.bindings.briefing_u0_signals import (
    BriefingMissingError,
    apps_research_call_required_at_u0,
    briefing_supplied_at_u0,
)
from apps_rg.runtime.bindings.l0_binding import l0_route_apps_rg, reset_route_profiles_cache
from apps_rg.runtime.bindings.l1_binding import l1_plan_apps_rg
from apps_rg.runtime.bindings.u0_profile_manifest import (
    l1_planning_profile_digest,
    l1_planning_profile_ref,
)


def _auth() -> AuthorityValidationReceipt:
    return AuthorityValidationReceipt(
        validation_timestamp=datetime.now(timezone.utc).isoformat(),
    )


def _pm() -> dict[str, str]:
    return {
        "l1_planning_profile_ref": l1_planning_profile_ref(),
        "l1_planning_profile_digest": l1_planning_profile_digest(allow_missing=False),
    }


def _vr(*, app_payload: dict) -> ValidatedRequest:
    return ValidatedRequest(
        request_id="r1",
        run_id="run1",
        app_id="apps_rg",
        task_class="resume_generation",
        trace_id="t1",
        payload_digest="sha256:test",
        authority_validation_receipt=_auth(),
        l5_certification_ref="test:valid:w6",
        app_payload=app_payload,
    )


def test_briefing_path_ref_counts_as_supplied() -> None:
    assert briefing_supplied_at_u0(
        {"policy_refs": {"briefing_artifact_ref": "apps_rg/config/targeting/brief.md"}}
    )


def test_inline_briefing_text_counts_as_supplied() -> None:
    assert briefing_supplied_at_u0({"briefing": {"briefing_text": "Company context."}})


def test_generate_scratch_product_visible_without_briefing_fails_closed() -> None:
    reset_route_profiles_cache()
    vr = _vr(
        app_payload={
            "task_spec": {"generation_mode": "generate_scratch"},
            "profile_manifest": _pm(),
        }
    )
    with pytest.raises(BriefingMissingError, match="apps_research delegation is disabled"):
        l1_plan_apps_rg(vr)


def test_generate_scratch_non_product_still_grounded_without_research() -> None:
    reset_route_profiles_cache()
    vr = _vr(
        app_payload={
            "task_spec": {"generation_mode": "generate_scratch"},
            "profile_manifest": _pm(),
            "non_product_certified": True,
        }
    )
    plan = l1_plan_apps_rg(vr)
    assert plan.grounding_required is True
    assert plan.apps_research_call_required is False
    route = l0_route_apps_rg(plan)
    assert route.grounding_required is True
    assert route.apps_research_call_required is False
    assert route.route_profile_ref.endswith("scratch_managed::v1")


def test_tailor_with_briefing_grounded_not_apps_research() -> None:
    reset_route_profiles_cache()
    vr = _vr(
        app_payload={
            "task_spec": {"generation_mode": "strategic_tailor"},
            "profile_manifest": _pm(),
            "policy_refs": {
                "briefing_artifact_ref": "apps_rg/config/targeting/brief.md",
            },
        }
    )
    plan = l1_plan_apps_rg(vr)
    assert plan.grounding_required is True
    assert plan.apps_research_call_required is False
    route = l0_route_apps_rg(plan)
    assert route.apps_research_call_required is False
    assert route.route_profile_ref.endswith("full_resume_managed::v1")


def test_apps_research_call_helper_matches_plan() -> None:
    vr = _vr(
        app_payload={
            "task_spec": {"generation_mode": "section_regen"},
            "profile_manifest": _pm(),
        }
    )
    assert apps_research_call_required_at_u0(vr, active_generation_mode=True) is False
