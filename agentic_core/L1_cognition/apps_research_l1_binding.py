"""L1 cognition binding for apps_research `company_brief` task class.

Per plan apps-research-golden-template-adoption-ag9.

L1 is the SECOND stage. Its job is to:
1. Consume ValidatedRequest.app_payload (never the raw ingress payload).
2. Read the apps_research planning profile.
3. Emit a typed L1PlanContract with task plan, capabilities, routing flags.

apps_research is R3_SIMPLE_GROUNDED_READ:
  grounding_required=True, model_generation_required=True,
  write_authority_present=False.
"""
from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timezone
from typing import Any, Mapping

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.contracts.posture import POSTURE_READ_ONLY

_LOGGER = logging.getLogger(__name__)

APPS_RESEARCH_L1_CERT_REF: str = "l1-apps-research-company-brief-ag9"

# Task plan steps for company_brief generation
_COMPANY_BRIEF_TASK_PLAN: tuple[str, ...] = (
    "validate_ingress_payload",
    "resolve_depth_profile",
    "retrieve_c0_evidence",
    "assemble_prompt_via_pa",
    "execute_synthesis_via_l2",
    "finalize_brief_via_exit",
)

_REQUIRED_CAPABILITIES: tuple[str, ...] = (
    "c0_evidence_retrieval",
    "prompt_assembly",
    "qwen_vllm_inference",
    "artifact_write",
)


def _extract_task_spec(app_payload: Mapping[str, Any]) -> dict[str, Any]:
    """Project task_spec from app_payload for downstream routing."""
    return {
        "generation_mode": "company_brief_synthesis",
        "capability_requirements": list(_REQUIRED_CAPABILITIES),
        "target_company": app_payload.get("target_company") or "",
        "target_role": app_payload.get("target_role") or "",
        "depth": app_payload.get("depth")
            or (app_payload.get("user_constraints") or {}).get("depth", "standard"),
    }


def _extract_query_spec(app_payload: Mapping[str, Any]) -> dict[str, Any]:
    """Project query_spec from app_payload — identity hashes and target tuple."""
    topic = (
        app_payload.get("topic")
        or (app_payload.get("user_constraints") or {}).get("topic", "")
        or app_payload.get("target_company", "")
    )
    target_company = app_payload.get("target_company") or ""
    target_role = app_payload.get("target_role") or ""
    topic_hash = hashlib.sha256(topic.encode("utf-8")).hexdigest() if topic else ""
    return {
        "topic": topic,
        "topic_hash": topic_hash,
        "target_company": target_company,
        "target_role": target_role,
        "target_tuple": f"{target_company}|{target_role}",
        "manual_brief_path": app_payload.get("manual_brief_path") or "",
    }


def _extract_support_expectation(app_payload: Mapping[str, Any]) -> dict[str, Any]:
    """Project support_expectation from app_payload."""
    return {
        "grounding_required": True,
        "provenance_required": True,
        "fact_check_required": False,
        "min_evidence_items": 1,
    }


def _extract_output_expectation(app_payload: Mapping[str, Any]) -> dict[str, Any]:
    """Project output_expectation from app_payload."""
    prefs = dict(app_payload.get("output_preferences") or {})
    return {
        "output_format": prefs.get("format", "json"),
        "schema_version": "company_brief_v1",
        "provenance_required": True,
        "fact_checked_required": False,
    }


def _extract_policy_refs(app_payload: Mapping[str, Any]) -> dict[str, str]:
    """Project policy_refs from app_payload."""
    return {
        "manifest_digest": app_payload.get("payload_digest", ""),
        "prompt_ref": "apps_research_prompt_bom_v1",
        "l0_route_ref": "R3_SIMPLE_GROUNDED_READ",
        "spec_ref": "company_brief_synthesis_v1",
        "thresholds_ref": "apps_research_default_thresholds",
    }


def l1_plan_apps_research(validated_request: ValidatedRequest) -> L1PlanContract:
    """Emit L1PlanContract for apps_research company_brief task.

    Reads exclusively from validated_request.app_payload. Does NOT re-read
    the raw ingress payload or any environment state.

    Returns a fully-typed L1PlanContract. Raises ValueError on bad input.
    """
    if not isinstance(validated_request, ValidatedRequest):
        raise TypeError(
            f"l1_plan_apps_research: expected ValidatedRequest, got {type(validated_request)}"
        )

    app_payload = validated_request.app_payload or {}

    task_spec = _extract_task_spec(app_payload)
    query_spec = _extract_query_spec(app_payload)
    support_expectation = _extract_support_expectation(app_payload)
    output_expectation = _extract_output_expectation(app_payload)
    policy_refs = _extract_policy_refs(app_payload)

    planning_ts = datetime.now(timezone.utc).isoformat()

    _LOGGER.debug(
        "L1 apps_research plan: topic=%r depth=%r",
        query_spec.get("topic", ""),
        task_spec.get("depth", ""),
    )

    return L1PlanContract(
        request_id=validated_request.request_id,
        run_id=validated_request.run_id,
        app_id="apps_research",
        trace_id=validated_request.trace_id,
        task_plan=_COMPANY_BRIEF_TASK_PLAN,
        required_capabilities=_REQUIRED_CAPABILITIES,
        grounding_required=True,
        model_generation_required=True,
        write_authority_present=False,
        tenant_id=validated_request.tenant_id,
        profile_manifest_digest=app_payload.get("payload_digest", ""),
        target_level=validated_request.target_level or "",
        task_spec=task_spec,
        query_spec=query_spec,
        support_expectation=support_expectation,
        output_expectation=output_expectation,
        policy_refs=policy_refs,
        planning_timestamp=planning_ts,
        schema_version="AG9.L1.1",
        posture=POSTURE_READ_ONLY,
        l5_certification_ref=APPS_RESEARCH_L1_CERT_REF,
    )


__all__ = [
    "APPS_RESEARCH_L1_CERT_REF",
    "l1_plan_apps_research",
]
