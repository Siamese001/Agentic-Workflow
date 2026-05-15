"""L1 binding for apps_rg resume_generation task class.

Exports l1_plan_apps_rg(validated_request) -> L1PlanContract.

Deterministic only. No C0, PA, L2, or provider calls.
"""
from __future__ import annotations

import logging
from typing import Any, Mapping

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract

_LOGGER = logging.getLogger(__name__)

APPS_RG_L1_CERT_REF = "apps_rg::l1::resume_generation::v1"

# Full resume generation modes: all work-shape hints True
_FULL_RESUME_GENERATION_MODES = frozenset({
    "strategic_tailor",
    "tailor_existing",
    "generate_scratch",
})

# Single-section or correction modes: all work-shape hints False
_SINGLE_SECTION_MODES = frozenset({
    "section_regen",
    "healing_fact_check",
})


def l1_plan_apps_rg(validated_request: ValidatedRequest) -> L1PlanContract:
    """Generate L1PlanContract from ValidatedRequest.

    Deterministic planning only. No external calls.

    Args:
        validated_request: U0-validated request with payload metadata.

    Returns:
        L1PlanContract with planning decisions and routing flags.
    """
    # Extract generation mode from app_payload if present
    app_payload = getattr(validated_request, "app_payload", None) or {}
    generation_mode = _extract_generation_mode(app_payload)

    # Derive work-shape hints based on generation mode
    work_shape_hints = _derive_work_shape_hints(generation_mode)

    # Build non-authority assertion (all True for apps_rg L1)
    non_authority_assertion = {
        "no_evidence_retrieval": True,
        "no_pa_assembly": True,
        "no_model_call": True,
        "no_c0_import": True,
    }

    # Extract profile refs for planning_prior_refs
    planning_prior_refs = _extract_planning_prior_refs(app_payload)

    # Build advisory route hints (not route authority)
    route_hints = _build_advisory_route_hints(generation_mode)

    # Extract prompt BOM refs
    prompt_bom_refs = _extract_prompt_bom_refs(app_payload)

    # Build core planning fields
    task_plan = _derive_task_plan(generation_mode)
    required_capabilities = _derive_capabilities(generation_mode)

    # Extract L5 cert ref from validated request (U0→L1 handoff)
    l5_cert_ref = getattr(validated_request, "l5_certification_ref", None) or ""

    return L1PlanContract(
        request_id=validated_request.request_id,
        run_id=validated_request.run_id,
        app_id=validated_request.app_id,
        trace_id=validated_request.trace_id,
        task_plan=task_plan,
        required_capabilities=required_capabilities,
        grounding_required=_needs_grounding(generation_mode),
        model_generation_required=_needs_model_generation(generation_mode),
        write_authority_present=False,
        profile_manifest_digest=validated_request.payload_digest,
        tenant_id=getattr(validated_request, "tenant_id", ""),
        target_level=_extract_target_level(app_payload),
        # Work-shape hints
        multiple_work_units_hint=work_shape_hints["multiple_work_units_hint"],
        merge_required_hint=work_shape_hints["merge_required_hint"],
        per_unit_quality_selection_hint=work_shape_hints["per_unit_quality_selection_hint"],
        candidate_generation_expected_hint=work_shape_hints["candidate_generation_expected_hint"],
        # W3 fields
        non_authority_assertion=non_authority_assertion,
        planning_prior_refs=planning_prior_refs,
        route_hints=route_hints,
        prompt_bom_refs=prompt_bom_refs,
        judge_eval_expectation_refs=(),  # Empty for now
        # Policy refs from payload if available
        policy_refs=_extract_policy_refs(app_payload),
        # L5 certification ref from U0
        l5_certification_ref=l5_cert_ref,
    )


def _derive_work_shape_hints(generation_mode: str) -> Mapping[str, bool]:
    """Derive work-shape hints from generation mode.

    Full resume modes: all hints True.
    Single-section/correction modes: all hints False.
    Unknown mode: all hints False (conservative).
    """
    if generation_mode in _FULL_RESUME_GENERATION_MODES:
        return {
            "multiple_work_units_hint": True,
            "merge_required_hint": True,
            "per_unit_quality_selection_hint": True,
            "candidate_generation_expected_hint": True,
        }
    # Single-section modes and unknown: conservative (all False)
    return {
        "multiple_work_units_hint": False,
        "merge_required_hint": False,
        "per_unit_quality_selection_hint": False,
        "candidate_generation_expected_hint": False,
    }


def _extract_generation_mode(app_payload: Mapping[str, Any]) -> str:
    """Extract generation_mode from app_payload."""
    if not app_payload:
        return ""
    # Try task_spec first
    task_spec = app_payload.get("task_spec", {})
    mode = task_spec.get("generation_mode", "")
    if mode:
        return mode
    # Fallback: check direct field
    return app_payload.get("generation_mode", "")


def _extract_target_level(app_payload: Mapping[str, Any]) -> str:
    """Extract target_level from app_payload."""
    if not app_payload:
        return ""
    query_spec = app_payload.get("query_spec", {})
    return query_spec.get("target_level", "")


def _extract_planning_prior_refs(app_payload: Mapping[str, Any]) -> tuple[str, ...]:
    """Extract planning prior refs from app_payload."""
    if not app_payload:
        return ()
    # Check for explicit prior refs
    prior_refs = app_payload.get("planning_prior_refs", [])
    if prior_refs:
        return tuple(str(r) for r in prior_refs)
    # Check profile_manifest for rg_planning_profile ref
    profile_manifest = app_payload.get("profile_manifest", {})
    planning_ref = profile_manifest.get("rg_planning_profile")
    if planning_ref:
        return (str(planning_ref),)
    # Canonical app-owned default
    return ("apps_rg/config/domain_contract/rg_planning_profile.yaml",)


def _extract_prompt_bom_refs(app_payload: Mapping[str, Any]) -> tuple[str, ...]:
    """Extract prompt BOM refs from app_payload."""
    if not app_payload:
        return ()
    # Check policy_refs for prompt_registry ref
    policy_refs = app_payload.get("policy_refs", {})
    registry_ref = policy_refs.get("prompt_registry_ref")
    if registry_ref:
        return (str(registry_ref),)
    # Check profile_manifest
    profile_manifest = app_payload.get("profile_manifest", {})
    registry_ref = profile_manifest.get("prompt_registry_ref")
    if registry_ref:
        return (str(registry_ref),)
    return ()


def _extract_policy_refs(app_payload: Mapping[str, Any]) -> Mapping[str, str]:
    """Extract policy refs from app_payload."""
    if not app_payload:
        return {}
    policy_refs = app_payload.get("policy_refs", {})
    if policy_refs:
        return {k: str(v) for k, v in policy_refs.items()}
    return {}


def _build_advisory_route_hints(generation_mode: str) -> Mapping[str, str]:
    """Build advisory route hints (not route authority)."""
    hints: dict[str, str] = {}
    if generation_mode in _FULL_RESUME_GENERATION_MODES:
        hints["execution_shape_hint"] = "multi_work_unit_managed_candidate"
    elif generation_mode in _SINGLE_SECTION_MODES:
        hints["execution_shape_hint"] = "single_work_unit_direct"
    return hints


def _derive_task_plan(generation_mode: str) -> tuple[str, ...]:
    """Derive task plan from generation mode."""
    base_plan = (
        "validate_ingress",
        "load_profiles",
    )
    if generation_mode in _FULL_RESUME_GENERATION_MODES:
        return base_plan + (
            "collect_evidence",
            "generate_resume",
            "assemble_output",
            "exit_eval",
        )
    elif generation_mode in _SINGLE_SECTION_MODES:
        return base_plan + (
            "collect_evidence",
            "generate_section",
            "assemble_output",
            "exit_eval",
        )
    # Unknown mode: conservative minimal plan
    return base_plan + ("exit_eval",)


def _derive_capabilities(generation_mode: str) -> tuple[str, ...]:
    """Derive required capabilities from generation mode."""
    caps = ["ingress_validation"]
    if generation_mode in _FULL_RESUME_GENERATION_MODES or generation_mode in _SINGLE_SECTION_MODES:
        caps.extend(["evidence_collection", "model_generation"])
    return tuple(caps)


def _needs_grounding(generation_mode: str) -> bool:
    """Determine if C0 evidence collection is required."""
    # All known modes need grounding; unknown conservatively does not
    return generation_mode in _FULL_RESUME_GENERATION_MODES or generation_mode in _SINGLE_SECTION_MODES


def _needs_model_generation(generation_mode: str) -> bool:
    """Determine if L2 model generation is required."""
    return generation_mode in _FULL_RESUME_GENERATION_MODES or generation_mode in _SINGLE_SECTION_MODES


__all__ = [
    "APPS_RG_L1_CERT_REF",
    "l1_plan_apps_rg",
    "_derive_work_shape_hints",
    "_FULL_RESUME_GENERATION_MODES",
    "_SINGLE_SECTION_MODES",
]
