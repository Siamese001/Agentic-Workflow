"""W3 — L1 validation receipt + ambiguity register; L0 route_digest + hmac_sig."""

from __future__ import annotations

import json

from apps_rg.runtime.bindings.l0_binding import l0_route_apps_rg
from apps_rg.runtime.bindings.l1_binding import l1_plan_apps_rg
from apps_rg.runtime.bindings.l0_route_evidence import compute_route_digest
from apps_rg.runtime.bindings.u0_binding import u0_validate_apps_rg
from apps_rg.runtime.dispatch.apps_rg_dispatch import apps_rg_parse


def _thin(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "app_id": "apps_rg",
        "task_class": "resume_generation",
        "target_company": "Acme Corp",
        "target_role": "Director of Engineering",
        "target_level": "EXECUTIVE",
        "source_resume_text": "Resume body for W3 evidence test.",
        "job_description_text": "JD body for W3 evidence test.",
    }
    base.update(overrides)
    return base


def test_l1_emits_validation_receipt_id_and_ambiguity_register_when_signals_present() -> None:
    env = apps_rg_parse(_thin(target_level=""))
    vr = u0_validate_apps_rg(env)
    plan = l1_plan_apps_rg(vr)
    assert plan.validation_receipt_id.startswith("l1val-")
    assert plan.ambiguity_register.get("entries")
    codes = {e["code"] for e in plan.ambiguity_register["entries"]}
    assert "TARGET_LEVEL_UNSPECIFIED" in codes


def test_l1_validation_receipt_id_stable_for_same_input() -> None:
    stable = _thin(
        request_id="req-w3-stable",
        run_id="run-w3-stable",
        trace_id="trace-w3-stable",
    )
    env_a = apps_rg_parse(stable)
    env_b = apps_rg_parse(dict(stable))
    plan_a = l1_plan_apps_rg(u0_validate_apps_rg(env_a))
    plan_b = l1_plan_apps_rg(u0_validate_apps_rg(env_b))
    assert plan_a.validation_receipt_id == plan_b.validation_receipt_id


def test_l0_emits_route_digest_and_hmac_sig() -> None:
    env = apps_rg_parse(_thin())
    plan = l1_plan_apps_rg(u0_validate_apps_rg(env))
    route = l0_route_apps_rg(plan)
    assert len(route.route_digest) == 64
    assert len(route.hmac_sig) == 64
    assert route.signature == route.hmac_sig


def test_route_digest_deterministic_for_same_plan() -> None:
    env = apps_rg_parse(_thin())
    plan = l1_plan_apps_rg(u0_validate_apps_rg(env))
    route_a = l0_route_apps_rg(plan)
    route_b = l0_route_apps_rg(plan)
    assert route_a.route_digest == route_b.route_digest
    assert route_a.hmac_sig == route_b.hmac_sig


def test_route_digest_changes_when_apps_research_call_changes() -> None:
    env = apps_rg_parse(_thin())
    vr = u0_validate_apps_rg(env)
    plan_with_brief = l1_plan_apps_rg(vr)
    from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract

    plan_no_brief = L1PlanContract(
        request_id=plan_with_brief.request_id,
        run_id=plan_with_brief.run_id,
        app_id=plan_with_brief.app_id,
        trace_id=plan_with_brief.trace_id,
        task_plan=plan_with_brief.task_plan,
        required_capabilities=plan_with_brief.required_capabilities,
        grounding_required=True,
        apps_research_call_required=True,
        model_generation_required=plan_with_brief.model_generation_required,
        l5_certification_ref=plan_with_brief.l5_certification_ref,
        task_spec=plan_with_brief.task_spec,
        merge_required_hint=plan_with_brief.merge_required_hint,
        validation_receipt_id=plan_with_brief.validation_receipt_id,
    )
    plan_brief_supplied = L1PlanContract(
        request_id=plan_with_brief.request_id,
        run_id=plan_with_brief.run_id,
        app_id=plan_with_brief.app_id,
        trace_id=plan_with_brief.trace_id,
        task_plan=plan_with_brief.task_plan,
        required_capabilities=plan_with_brief.required_capabilities,
        grounding_required=True,
        apps_research_call_required=False,
        model_generation_required=plan_with_brief.model_generation_required,
        l5_certification_ref=plan_with_brief.l5_certification_ref,
        task_spec=plan_with_brief.task_spec,
        merge_required_hint=plan_with_brief.merge_required_hint,
        validation_receipt_id=plan_with_brief.validation_receipt_id,
    )
    route_delegated = l0_route_apps_rg(plan_no_brief)
    route_uploaded = l0_route_apps_rg(plan_brief_supplied)
    assert route_delegated.route_digest != route_uploaded.route_digest


def test_managed_workflow_allows_l3_only() -> None:
    env = apps_rg_parse(_thin(generation_mode="strategic_tailor"))
    plan = l1_plan_apps_rg(u0_validate_apps_rg(env))
    route = l0_route_apps_rg(plan)
    if route.execution_form.upper() == "MANAGED_WORKFLOW" and route.l3_required:
        assert route.allowed_next_stage == frozenset({"L3"})


def test_l3_scope_doc_exists() -> None:
    from pathlib import Path

    doc = Path("apps_rg/config/domain_contract/L3_managed_workflow_scope.md")
    assert doc.is_file()
    text = doc.read_text(encoding="utf-8")
    assert "core-owned" in text.lower()
    assert "agentic_core/L3_orchestration" in text
