"""Product-visible apps_rg generation requires briefing and apps_research flagging."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from agentic_core.L0_routing.u0_intake_validator import AuthorityValidationReceipt
from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest

from apps_rg.runtime.bindings.briefing_u0_signals import BriefingMissingError
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


def _vr(app_payload: dict) -> ValidatedRequest:
    return ValidatedRequest(
        request_id="req-brief",
        run_id="run-brief",
        app_id="apps_rg",
        task_class="resume_generation",
        trace_id="trace-brief",
        payload_digest="sha256:test",
        authority_validation_receipt=_auth(),
        l5_certification_ref="test:valid:w6",
        app_payload=app_payload,
    )


def _payload(mode: str, **extra: object) -> dict:
    payload = {
        "task_spec": {"generation_mode": mode},
        "profile_manifest": _pm(),
    }
    payload.update(extra)
    return payload


@pytest.mark.parametrize("mode", ["strategic_tailor", "generate_scratch"])
def test_product_visible_full_generation_without_briefing_fails_closed(mode: str) -> None:
    with pytest.raises(BriefingMissingError, match="apps_research is required"):
        l1_plan_apps_rg(_vr(_payload(mode)))


def test_product_visible_section_regen_without_briefing_fails_closed() -> None:
    with pytest.raises(BriefingMissingError, match="requires an uploaded briefing"):
        l1_plan_apps_rg(_vr(_payload("section_regen", product_visible=True)))


@pytest.mark.parametrize(
    "flag",
    [
        {"fixture_dev_only": True},
        {"non_product_certified": True},
    ],
)
def test_section_regen_without_briefing_allowed_only_for_non_product_paths(flag: dict) -> None:
    plan = l1_plan_apps_rg(_vr(_payload("section_regen", **flag)))
    assert plan.apps_research_call_required is False


def test_valid_briefing_artifact_ref_passes() -> None:
    plan = l1_plan_apps_rg(
        _vr(_payload("strategic_tailor", briefing_artifact_ref="artifact:brief"))
    )
    assert plan.apps_research_call_required is True


def test_valid_manual_brief_path_passes() -> None:
    plan = l1_plan_apps_rg(
        _vr(_payload("generate_scratch", manual_brief_path="brief.md"))
    )
    assert plan.apps_research_call_required is True


def test_valid_inline_authoritative_briefing_text_passes() -> None:
    plan = l1_plan_apps_rg(
        _vr(_payload("section_regen", briefing={"briefing_text": "Authoritative brief."}))
    )
    assert plan.apps_research_call_required is True


def test_apps_research_call_required_field_is_true_when_contract_field_exists() -> None:
    plan = l1_plan_apps_rg(
        _vr(_payload("healing_fact_check", briefing_text="Authoritative brief."))
    )
    assert hasattr(plan, "apps_research_call_required")
    assert plan.apps_research_call_required is True
