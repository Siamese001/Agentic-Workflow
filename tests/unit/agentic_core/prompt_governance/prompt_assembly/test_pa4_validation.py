"""Unit tests for PA.4 17-check validation matrix."""

from __future__ import annotations

from agentic_core.prompt_governance.prompt_assembly.input_contracts import (
    upstream_bundle_from_dicts,
)
from agentic_core.prompt_governance.prompt_assembly.pa1_bom_resolver import resolve_bom
from agentic_core.prompt_governance.prompt_assembly.pa2_slot_composition import compose_slots
from agentic_core.prompt_governance.prompt_assembly.pa4_validation import validate_pa4


def _ok_bundle(**overrides):
    plan = {"plan_id": "p1", "policy_hash": "ph", "grounding_required": False}
    plan.update(overrides.get("plan", {}))
    route = {
        "route_id": "R3",
        "execution_form": "SINGLE_STEP",
        "policy_hash": "ph",
        "support_target": "loose",
        "model_id": "m",
        "provider_lane": "anthropic",
    }
    route.update(overrides.get("route", {}))
    evidence = {"status": "PASS", "support_score": 0.9, "policy_hash": "ph"}
    evidence.update(overrides.get("evidence", {}))
    gov = {
        "system_version_hash": "sv",
        "policy_hash": "ph",
        "role_fences": ("MUST",),
        "response_schema_contract": {
            "type": "object",
            "version": "v1",
            "can_abstain": True,
            "can_cite": True,
        },
        "citation_mode": "optional",
        "allowed_tool_posture": "limited",
    }
    gov.update(overrides.get("gov", {}))
    exec_m = {"replay_key": "rk", "policy_hash": "ph", "raw_user_task": "task"}
    exec_m.update(overrides.get("exec_m", {}))
    return upstream_bundle_from_dicts(
        plan_contract=plan,
        route_contract=route,
        evidence_contract=evidence,
        governance=gov,
        execution_metadata=exec_m,
    )


def _ok_sources(**overrides):
    src = {
        "s0_content": "S",
        "d0_fences": ("MUST",),
        "i0_content": "I",
    }
    src.update(overrides)
    return src


def _full(bundle, sources):
    bom = resolve_bom(bundle, sources)
    comp = compose_slots(bom)
    return bom, comp


def test_pa4_all_pass_minimal():
    bundle = _ok_bundle()
    bom, comp = _full(bundle, _ok_sources())
    report = validate_pa4(bundle=bundle, bom=bom, stack=comp.stack)
    assert report.overall_passed is True
    assert report.failed_count == 0


def test_pa4_evidence_status_blocked_fails():
    bundle = _ok_bundle(
        plan={"grounding_required": True}, evidence={"status": "BLOCKED", "support_score": 0.0}
    )
    bom, comp = _full(bundle, _ok_sources())
    report = validate_pa4(bundle=bundle, bom=bom, stack=comp.stack)
    assert "evidence_status_consistent_with_plan" in report.failed_ids


def test_pa4_unresolved_gaps_with_pass_evidence_fails():
    bundle = _ok_bundle(
        plan={"grounding_required": True},
        evidence={"status": "PASS", "support_score": 0.9, "unresolved_gaps": ("missing-X",)},
    )
    bom, comp = _full(bundle, _ok_sources())
    report = validate_pa4(bundle=bundle, bom=bom, stack=comp.stack)
    assert "unresolved_gaps_present_or_grounding_not_required" in report.failed_ids


def test_pa4_support_score_below_threshold_fails():
    bundle = _ok_bundle(plan={"grounding_required": True}, evidence={"status": "PASS", "support_score": 0.2})
    bom, comp = _full(bundle, _ok_sources())
    report = validate_pa4(bundle=bundle, bom=bom, stack=comp.stack, support_threshold=0.6)
    assert "support_score_meets_threshold" in report.failed_ids


def test_pa4_citation_required_but_schema_lacks():
    bundle = _ok_bundle(
        gov={
            "response_schema_contract": {"type": "object", "version": "v1"},  # no can_cite
            "citation_mode": "required",
        },
    )
    bom, comp = _full(bundle, _ok_sources())
    report = validate_pa4(bundle=bundle, bom=bom, stack=comp.stack)
    assert "citation_mode_respected" in report.failed_ids or "r0_can_represent_citations" in report.failed_ids


def test_pa4_policy_hash_mismatch_fails():
    bundle = _ok_bundle(route={"policy_hash": "OTHER"})
    bom, comp = _full(bundle, _ok_sources())
    report = validate_pa4(bundle=bundle, bom=bom, stack=comp.stack)
    assert "policy_hash_consistent_across_inputs" in report.failed_ids


def test_pa4_capability_token_missing_when_tools_bound():
    bundle = _ok_bundle()
    src = _ok_sources(
        tools=[{"name": "search"}],
        tool_registry=("search",),
        tools_allowed_by_token=("search",),
    )
    bom, comp = _full(bundle, src)
    report = validate_pa4(bundle=bundle, bom=bom, stack=comp.stack)
    assert "capability_token_present_when_tools_bound" in report.failed_ids


def test_pa4_tool_posture_none_with_tools_fails():
    bundle = _ok_bundle(gov={"allowed_tool_posture": "none"})
    src = _ok_sources(
        tools=[{"name": "search"}],
        tool_registry=("search",),
        tools_allowed_by_token=("search",),
    )
    bom, comp = _full(bundle, src)
    report = validate_pa4(bundle=bundle, bom=bom, stack=comp.stack)
    assert "allowed_tool_posture_respected" in report.failed_ids


def test_pa4_seventeen_total_checks():
    bundle = _ok_bundle()
    bom, comp = _full(bundle, _ok_sources())
    report = validate_pa4(bundle=bundle, bom=bom, stack=comp.stack)
    assert len(report.checks) == 17
    assert report.passed_count + report.failed_count == 17
