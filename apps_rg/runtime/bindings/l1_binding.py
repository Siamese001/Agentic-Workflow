"""L1 binding for the apps_rg ``resume_generation`` task class.

Exports ``l1_plan_apps_rg(validated_request) -> L1PlanContract``.
Deterministic only. No C0, PA, L2, tool, provider, or write calls.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Mapping

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from apps_rg.runtime.bindings.l1_planning_capsule import (
    build_apps_rg_l1_planning_capsule,
    verify_planning_profile_ref_digest,
)

_LOGGER = logging.getLogger(__name__)

APPS_RG_L1_CERT_REF = "apps_rg::l1::resume_generation::v1"

_FULL_RESUME_GENERATION_MODES = frozenset(
    {"strategic_tailor", "tailor_existing", "generate_scratch"}
)
_SINGLE_SECTION_MODES = frozenset({"section_regen", "healing_fact_check"})


def l1_plan_apps_rg(validated_request: ValidatedRequest) -> L1PlanContract:
    """Generate a deterministic, integrity-bound L1 plan from ``ValidatedRequest``."""

    app_payload = getattr(validated_request, "app_payload", None) or {}
    if not app_payload:
        raise ValueError(
            "missing required keys: app_payload is empty; U0 must synthesize "
            "task_spec, query_spec, support_expectation, and output_expectation."
        )

    generation_mode = _extract_generation_mode(app_payload)
    work_shape_hints = _derive_work_shape_hints(generation_mode)
    non_authority_assertion = {
        "no_evidence_retrieval": True,
        "no_pa_assembly": True,
        "no_model_call": True,
        "no_c0_import": True,
    }

    task_spec = dict(app_payload.get("task_spec") or {})
    query_spec = dict(app_payload.get("query_spec") or {})
    support_expectation = dict(app_payload.get("support_expectation") or {})
    output_expectation = dict(app_payload.get("output_expectation") or {})
    policy_src = app_payload.get("policy_refs")
    if isinstance(policy_src, Mapping) and policy_src:
        policy_refs_out: Mapping[str, str] = {
            key: str(value) for key, value in policy_src.items()
        }
    else:
        policy_refs_out = _extract_policy_refs(app_payload)

    work_shape = (
        "full_resume_generation"
        if work_shape_hints["merge_required_hint"]
        else "narrow_regeneration"
    )
    task_shape = generation_mode or "unknown"
    route_profile_ref = "apps_rg/config/domain_contract/route_profiles.yaml"
    replay_key = str(getattr(validated_request, "replay_key", "") or "")

    pm = (
        app_payload.get("profile_manifest")
        if isinstance(app_payload.get("profile_manifest"), Mapping)
        else {}
    )
    from apps_rg.runtime.bindings.u0_profile_manifest import (
        l1_planning_profile_digest,
        l1_planning_profile_ref,
    )

    planning_profile_ref = str(
        pm.get("l1_planning_profile_ref") or l1_planning_profile_ref()
    ).strip()
    planning_digest = str(pm.get("l1_planning_profile_digest") or "").strip()
    if not planning_digest:
        if "l1_planning_profile_digest" in pm and not os.environ.get(
            "APPS_RG_L1_ALLOW_EMPTY_PROFILE_DIGEST", ""
        ).strip():
            raise ValueError(
                "l1_plan_apps_rg: U0-declared l1_planning_profile_digest is empty"
            )
        planning_digest = l1_planning_profile_digest(allow_missing=False)
    _, planning_profile_ref, planning_digest = verify_planning_profile_ref_digest(
        planning_profile_ref,
        planning_digest,
    )

    manifest_digest = str(pm.get("manifest_digest") or validated_request.payload_digest)
    capsule = build_apps_rg_l1_planning_capsule(
        app_payload=app_payload,
        request_id=validated_request.request_id,
        run_id=validated_request.run_id,
        trace_id=validated_request.trace_id,
        replay_key=replay_key,
        planning_profile_ref=planning_profile_ref,
        planning_profile_digest=planning_digest,
    )

    from apps_rg.runtime.bindings.l1_plan_evidence import build_validation_receipt_id

    validation_receipt_id = build_validation_receipt_id(
        request_id=validated_request.request_id,
        profile_manifest_digest=manifest_digest,
        planning_profile_digest=planning_digest,
        capsule_digest=str(capsule["capsule_digest"]),
    )

    task_spec["apps_rg_planning_capsule_ref"] = capsule["capsule_digest"]
    task_spec["apps_rg_planning_capsule"] = capsule
    task_spec["apps_rg_planning_status"] = capsule["planning_status"]
    support_expectation["apps_rg_evidence_plan_ref"] = capsule["capsule_digest"]
    output_expectation["apps_rg_completion_criteria_ref"] = capsule["capsule_digest"]
    ambiguity_register = capsule["ambiguity_register"]

    route_hints = _build_advisory_route_hints(
        generation_mode,
        capsule_route_feature_hints=capsule.get("route_feature_hints"),
    )

    active_generation = (
        generation_mode in _FULL_RESUME_GENERATION_MODES
        or generation_mode in _SINGLE_SECTION_MODES
    )
    non_product_path = bool(
        app_payload.get("fixture_dev_only")
        or app_payload.get("non_product_certified")
        or app_payload.get("product_visible") is False
    )
    from apps_rg.runtime.bindings.briefing_u0_signals import (
        apps_research_call_required_at_u0,
        briefing_validate_or_raise,
    )

    apps_research_required = apps_research_call_required_at_u0(
        validated_request,
        active_generation_mode=active_generation,
    )
    briefing_validate_or_raise(
        validated_request,
        active_generation_mode=active_generation,
        product_visible=not non_product_path,
        non_product_certified=non_product_path,
        context=f"generation_mode={generation_mode or 'unknown'}",
    )

    planning_prior_refs = tuple(
        dict.fromkeys((*_extract_planning_prior_refs(app_payload), planning_profile_ref))
    )
    capsule_digest = str(capsule["capsule_digest"])
    audit_refs = (
        f"l1_capsule_digest:{capsule_digest}",
        f"l1_planning_profile_digest:{planning_digest}",
        f"l1_validation_receipt:{validation_receipt_id}",
    )

    return L1PlanContract(
        request_id=validated_request.request_id,
        run_id=validated_request.run_id,
        app_id=validated_request.app_id,
        trace_id=validated_request.trace_id,
        task_plan=_derive_task_plan(generation_mode),
        required_capabilities=_derive_capabilities(generation_mode),
        grounding_required=_resume_evidence_grounding_required(generation_mode),
        apps_research_call_required=apps_research_required,
        model_generation_required=_needs_model_generation(generation_mode),
        write_authority_present=False,
        profile_manifest_digest=validated_request.payload_digest,
        tenant_id=getattr(validated_request, "tenant_id", ""),
        target_level=_extract_target_level(app_payload),
        task_spec=task_spec,
        query_spec=query_spec,
        support_expectation=support_expectation,
        output_expectation=output_expectation,
        work_shape=work_shape,
        task_shape=task_shape,
        route_profile_ref=route_profile_ref,
        multiple_work_units_hint=work_shape_hints["multiple_work_units_hint"],
        merge_required_hint=work_shape_hints["merge_required_hint"],
        per_unit_quality_selection_hint=work_shape_hints[
            "per_unit_quality_selection_hint"
        ],
        candidate_generation_expected_hint=work_shape_hints[
            "candidate_generation_expected_hint"
        ],
        non_authority_assertion=non_authority_assertion,
        planning_prior_refs=planning_prior_refs,
        route_hints=route_hints,
        prompt_bom_refs=_extract_prompt_bom_refs(app_payload),
        judge_eval_expectation_refs=(),
        policy_refs=policy_refs_out,
        l5_certification_ref=str(
            getattr(validated_request, "l5_certification_ref", None) or ""
        ),
        replay_key=replay_key,
        validation_receipt_id=validation_receipt_id,
        ambiguity_register=ambiguity_register,
        audit_refs=audit_refs,
    )


def _derive_work_shape_hints(generation_mode: str) -> Mapping[str, bool]:
    """Derive advisory work-shape facts without selecting a route."""

    if generation_mode in _FULL_RESUME_GENERATION_MODES:
        return {
            "multiple_work_units_hint": True,
            "merge_required_hint": True,
            "per_unit_quality_selection_hint": True,
            "candidate_generation_expected_hint": True,
        }
    return {
        "multiple_work_units_hint": False,
        "merge_required_hint": False,
        "per_unit_quality_selection_hint": False,
        "candidate_generation_expected_hint": False,
    }


def _extract_generation_mode(app_payload: Mapping[str, Any]) -> str:
    if not app_payload:
        return ""
    task_spec = app_payload.get("task_spec", {})
    mode = task_spec.get("generation_mode", "") if isinstance(task_spec, Mapping) else ""
    return str(mode or app_payload.get("generation_mode", ""))


def _extract_target_level(app_payload: Mapping[str, Any]) -> str:
    if not app_payload:
        return ""
    query_spec = app_payload.get("query_spec", {})
    if not isinstance(query_spec, Mapping):
        return ""
    direct = str(query_spec.get("target_level") or "").strip()
    target = (
        query_spec.get("target")
        if isinstance(query_spec.get("target"), Mapping)
        else {}
    )
    return direct or str(
        target.get("level") or app_payload.get("target_level") or ""
    ).strip()


def _verify_l1_planning_profile_digest(app_payload: Mapping[str, Any]) -> None:
    """Compatibility helper: verify the exact profile ref and exact loaded bytes."""

    pm = app_payload.get("profile_manifest")
    if not isinstance(pm, Mapping):
        return
    if "l1_planning_profile_digest" not in pm and "l1_planning_profile_ref" not in pm:
        return
    from apps_rg.runtime.bindings.u0_profile_manifest import (
        l1_planning_profile_digest,
        l1_planning_profile_ref,
    )

    ref = str(pm.get("l1_planning_profile_ref") or l1_planning_profile_ref())
    digest = str(pm.get("l1_planning_profile_digest") or "")
    if not digest and os.environ.get(
        "APPS_RG_L1_ALLOW_EMPTY_PROFILE_DIGEST", ""
    ).strip():
        digest = l1_planning_profile_digest(allow_missing=False)
    verify_planning_profile_ref_digest(ref, digest)


def _extract_planning_prior_refs(app_payload: Mapping[str, Any]) -> tuple[str, ...]:
    if not app_payload:
        return ()
    prior_refs = app_payload.get("planning_prior_refs", [])
    if prior_refs:
        return tuple(str(ref) for ref in prior_refs)
    profile_manifest = app_payload.get("profile_manifest", {})
    if not isinstance(profile_manifest, Mapping):
        return ("apps_rg/profiles/rg_planning_profile.yaml",)
    l1_ref = profile_manifest.get("l1_planning_profile_ref")
    if l1_ref:
        return (str(l1_ref),)
    planning_ref = profile_manifest.get("rg_planning_profile")
    if planning_ref:
        return (str(planning_ref),)
    return ("apps_rg/profiles/rg_planning_profile.yaml",)


def _extract_prompt_bom_refs(app_payload: Mapping[str, Any]) -> tuple[str, ...]:
    if not app_payload:
        return ()
    policy_refs = app_payload.get("policy_refs", {})
    if isinstance(policy_refs, Mapping):
        registry_ref = policy_refs.get("prompt_registry_ref")
        if registry_ref:
            return (str(registry_ref),)
    profile_manifest = app_payload.get("profile_manifest", {})
    if isinstance(profile_manifest, Mapping):
        registry_ref = profile_manifest.get("prompt_registry_ref")
        if registry_ref:
            return (str(registry_ref),)
    return ()


def _extract_policy_refs(app_payload: Mapping[str, Any]) -> Mapping[str, str]:
    if not app_payload:
        return {}
    policy_refs = app_payload.get("policy_refs", {})
    if isinstance(policy_refs, Mapping) and policy_refs:
        return {key: str(value) for key, value in policy_refs.items()}
    return {}


def _build_advisory_route_hints(
    generation_mode: str,
    *,
    capsule_route_feature_hints: Mapping[str, Any] | None = None,
) -> Mapping[str, str]:
    """Build advisory features; L0 remains the sole route authority."""

    hints: dict[str, str] = {"authority_class": "ADVISORY_ONLY"}
    if generation_mode in _FULL_RESUME_GENERATION_MODES:
        hints["execution_shape_hint"] = "multi_work_unit_managed_candidate"
    elif generation_mode in _SINGLE_SECTION_MODES:
        hints["execution_shape_hint"] = "single_work_unit_direct"
    route_features = dict(capsule_route_feature_hints or {})
    feature_map = {
        "multi_work_unit": "multi_work_unit_hint",
        "merge_needed": "merge_needed_hint",
        "candidate_selection_needed": "candidate_selection_needed_hint",
        "grounding_needed": "grounding_needed_hint",
    }
    for src, dst in feature_map.items():
        if src in route_features:
            hints[dst] = "true" if bool(route_features[src]) else "false"
    risk = str(route_features.get("hitl_risk_hint") or "none")
    hints["hitl_risk_hint"] = risk
    hints["hitl_posture"] = risk
    return hints


def _derive_task_plan(generation_mode: str) -> tuple[str, ...]:
    base_plan = ("validate_ingress", "load_profiles")
    if generation_mode in _FULL_RESUME_GENERATION_MODES:
        return base_plan + (
            "collect_evidence",
            "generate_resume",
            "assemble_output",
            "exit_eval",
        )
    if generation_mode in _SINGLE_SECTION_MODES:
        return base_plan + (
            "collect_evidence",
            "generate_section",
            "assemble_output",
            "exit_eval",
        )
    return base_plan + ("exit_eval",)


def _derive_capabilities(generation_mode: str) -> tuple[str, ...]:
    caps = ["ingress_validation"]
    if (
        generation_mode in _FULL_RESUME_GENERATION_MODES
        or generation_mode in _SINGLE_SECTION_MODES
    ):
        caps.extend(["evidence_collection", "model_generation"])
    return tuple(caps)


def _resume_evidence_grounding_required(generation_mode: str) -> bool:
    return (
        generation_mode in _FULL_RESUME_GENERATION_MODES
        or generation_mode in _SINGLE_SECTION_MODES
    )


def _needs_model_generation(generation_mode: str) -> bool:
    return (
        generation_mode in _FULL_RESUME_GENERATION_MODES
        or generation_mode in _SINGLE_SECTION_MODES
    )


__all__ = [
    "APPS_RG_L1_CERT_REF",
    "l1_plan_apps_rg",
    "_derive_work_shape_hints",
    "_FULL_RESUME_GENERATION_MODES",
    "_SINGLE_SECTION_MODES",
]
