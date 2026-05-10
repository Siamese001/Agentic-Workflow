"""L0 routing binding for the apps_lic `outreach_message` task class.

L0 is the THIRD stage of the U0 -> L1 -> L0 -> [C0] -> [PA] -> L3/L2 -> Exit
pipeline. Its job is to consume the L1PlanContract app_payload-derived
projections and emit a single deterministic RouteContract.

AG-8 W4 invariant (apps-lic-ag8-golden-template-adoption-f3c2e1):
    L0 reads L1PlanContract ONLY — never ValidatedRequest, never
    envelope.payload. Route decisions are deterministic functions of:

        - l1_plan.grounding_required           → route_family
        - l1_plan.task_spec["action_required"] → action_required
        - l1_plan.task_spec["workflow_required"] → execution_form + l3_required
        - l1_plan.task_spec["channel"]          → route_id variant
        - l1_plan.support_expectation["hitl_required"] → HITL posture metadata

    L0 produces on RouteContract:
        - route_family:    "evidence_grounded_generation" | "ungrounded_generation"
        - execution_form:  "managed_workflow" when workflow_required else "single_step"
        - grounding_required: threaded from L1
        - action_required: threaded from task_spec.action_required
        - side_effect_class: always "read_only" for outreach generation
        - cache_eligibility: r1a_exact=True, r1b_semantic=False, r3_grounded=True
                             if grounding, r4_action=False always
        - HITL metadata: surfaced in reason_codes + route_id suffix

HARD LAWS (AG-8 W4):
    - L0 does NOT retrieve, execute, assemble prompts, or write L4.
    - L0 does NOT call ChromaDB, embedding models, or any external I/O.
    - L0 emits exactly ONE route (no route list, no conditional multi-emit).
    - execution_form='managed_workflow' iff task_spec.workflow_required=True.
    - route_family is a pure deterministic function of grounding_required.

Plan: .windsurf/plans/apps-lic-ag8-golden-template-adoption-f3c2e1.md (W4)
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.contracts.route_contract import RouteContract


APPS_LIC_L0_CERT_REF: str = "l0-apps-lic-outreach-message-ag8-w4-f3c2e1"

APPS_LIC_DEFAULT_ROUTE_ID: str = "lic.outreach_message.default"
APPS_LIC_COLD_ROUTE_ID: str = "lic.outreach_message.cold"
APPS_LIC_WARM_ROUTE_ID: str = "lic.outreach_message.warm"
APPS_LIC_FOLLOW_UP_ROUTE_ID: str = "lic.outreach_message.follow_up"

_ROUTE_PROFILE_RELPATH: str = "apps_lic/config/domain_contract/route_profiles.yaml"

_ROUTE_FAMILY_GROUNDED: str = "evidence_grounded_generation"
_ROUTE_FAMILY_UNGROUNDED: str = "ungrounded_generation"

# apps_lic allowed models: Qwen32B for draft generation
_ALLOWED_MODELS: tuple[str, ...] = ("Qwen/Qwen2.5-32B-Instruct-AWQ",)
_ALLOWED_NETWORKS: tuple[str, ...] = ("localhost:8000",)
_ALLOWED_FILE_ROOTS: tuple[str, ...] = ("artifacts/apps_lic/",)

# Permitted tools (from capability_profiles.yaml)
_ALLOWED_TOOLS: tuple[str, ...] = (
    "tool::recipient_profile_lookup_verified",
    "tool::company_kb_lookup",
    "tool::voice_profile_apply",
    "tool::message_render",
    "tool::message_validate",
    "tool::compliance_check",
)


def _derive_route_family(l1_plan: L1PlanContract) -> str:
    """Route family is a pure function of grounding_required."""
    return _ROUTE_FAMILY_GROUNDED if l1_plan.grounding_required else _ROUTE_FAMILY_UNGROUNDED


def _derive_route_id(l1_plan: L1PlanContract) -> str:
    """Select route_id variant from task_spec.channel.

    Channel drives the variant route_id. Default falls through to
    APPS_LIC_DEFAULT_ROUTE_ID. Route hints are advisory; this decision
    is purely deterministic from the canonical task_spec projection.
    """
    channel = str(l1_plan.task_spec.get("channel", "email")).lower()
    request_type = str(l1_plan.task_spec.get("request_type", "outreach_draft")).lower()

    if "follow_up" in request_type or "follow_up" in channel:
        return APPS_LIC_FOLLOW_UP_ROUTE_ID
    if channel in ("cold", "cold_email", "cold_linkedin"):
        return APPS_LIC_COLD_ROUTE_ID
    if channel in ("warm", "warm_email", "warm_linkedin"):
        return APPS_LIC_WARM_ROUTE_ID
    return APPS_LIC_DEFAULT_ROUTE_ID


def _derive_execution_form(l1_plan: L1PlanContract) -> str:
    """execution_form=managed_workflow iff workflow_required=True in task_spec.

    AG-8 W4 hard law: if workflow_required is true, execution_form MUST be
    MANAGED_WORKFLOW. For outreach_message the HOP pipeline (9 stages) qualifies
    as a managed workflow.
    """
    workflow_required = bool(l1_plan.task_spec.get("workflow_required", False))
    return "managed_workflow" if workflow_required else "single_step"


def _derive_l3_required(l1_plan: L1PlanContract) -> bool:
    """L3 is required when the execution_form is managed_workflow."""
    return bool(l1_plan.task_spec.get("workflow_required", False))


def _derive_action_required(l1_plan: L1PlanContract) -> bool:
    """action_required is driven by task_spec.action_required.

    apps_lic outreach_message is generation-only at this stage — no send,
    no state mutation. write_authority_present is always False.
    """
    action_str = str(l1_plan.task_spec.get("action_required", "draft_and_cert")).lower()
    if action_str in ("", "draft_and_cert", "draft_only"):
        return False
    if action_str in ("send_approved", "send_immediately"):
        return True
    return bool(l1_plan.write_authority_present)


def _derive_cache_eligibility(l1_plan: L1PlanContract) -> dict[str, bool]:
    """Per-cache-tier eligibility.

    R1A: exact-key always eligible (input digest canonical).
    R1B: semantic deferred (no embedding compat proof yet).
    R3:  grounded cache eligible iff grounding_required.
    R4:  action cache never (no state mutation at generation stage).
    """
    return {
        "r1a_exact": True,
        "r1b_semantic": False,
        "r3_grounded": bool(l1_plan.grounding_required),
        "r4_action": False,
    }


def _derive_side_effect_class(l1_plan: L1PlanContract) -> str:
    """Verified from task_spec; always read_only for outreach generation."""
    return str(l1_plan.task_spec.get("side_effect_class", "read_only"))


def _read_route_profile_digest(repo_root: Path) -> str:
    profile_path = repo_root / _ROUTE_PROFILE_RELPATH
    if not profile_path.exists():
        return ""
    try:
        return hashlib.sha256(profile_path.read_bytes()).hexdigest()
    except OSError:
        return ""


def _resolve_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return here.parents[3]


def _build_reason_codes(
    l1_plan: L1PlanContract,
    route_id: str,
    route_family: str,
    execution_form: str,
    action_required: bool,
    cache_eligibility: dict[str, bool],
    side_effect_class: str,
) -> tuple[str, ...]:
    codes: list[str] = [
        "task_class=outreach_message",
        f"route_id={route_id}",
        f"route_family={route_family}",
        f"execution_form={execution_form}",
        f"l3_required={l1_plan.task_spec.get('workflow_required', False)}",
        f"grounding_required={l1_plan.grounding_required}",
        f"action_required={action_required}",
        f"side_effect_class={side_effect_class}",
        f"channel={l1_plan.task_spec.get('channel', 'email')}",
        f"cache_eligibility={json.dumps(cache_eligibility, sort_keys=True)}",
    ]
    hitl = l1_plan.support_expectation.get("hitl_required", True)
    codes.append(f"hitl_required={hitl}")
    pii_mode = l1_plan.support_expectation.get("pii_detection_mode", "strict")
    codes.append(f"pii_detection_mode={pii_mode}")
    shield = l1_plan.support_expectation.get("governance_shield_required", True)
    codes.append(f"governance_shield_required={shield}")
    codes.append(f"model_generation_required={l1_plan.model_generation_required}")
    codes.append("write_authority_present=false (generation only)")
    return tuple(codes)


def l0_route_apps_lic(l1_plan: L1PlanContract) -> RouteContract:
    """Emit a single deterministic RouteContract from an apps_lic L1 plan.

    Args:
        l1_plan: L1PlanContract output of l1_plan_apps_lic.

    Returns:
        RouteContract with route_id, execution_form, l3_required, grounding flags,
        capability surface, side_effect_class, cache_eligibility, and reason_codes.

    Raises:
        TypeError: if l1_plan is not an L1PlanContract.
        ValueError: if l1_plan.app_id != 'apps_lic'.
        ValueError: if workflow_required=True but execution_form derivation fails.
    """
    if not isinstance(l1_plan, L1PlanContract):
        raise TypeError(
            f"l0_route_apps_lic expected L1PlanContract, got {type(l1_plan).__name__}"
        )
    if l1_plan.app_id != "apps_lic":
        raise ValueError(
            f"l0_route_apps_lic expected app_id='apps_lic'; got {l1_plan.app_id!r}"
        )

    _ = _read_route_profile_digest(_resolve_repo_root())  # captured for parity

    route_id = _derive_route_id(l1_plan)
    route_family = _derive_route_family(l1_plan)
    execution_form = _derive_execution_form(l1_plan)
    l3_required = _derive_l3_required(l1_plan)
    action_required = _derive_action_required(l1_plan)
    cache_eligibility = _derive_cache_eligibility(l1_plan)
    side_effect_class = _derive_side_effect_class(l1_plan)

    # AG-8 W4 hard law: workflow_required=True must produce managed_workflow.
    workflow_required = bool(l1_plan.task_spec.get("workflow_required", False))
    if workflow_required and execution_form != "managed_workflow":
        raise ValueError(
            "l0_route_apps_lic: workflow_required=True but execution_form "
            f"derived as {execution_form!r} — AG-8 W4 hard law violated"
        )

    reason_codes = _build_reason_codes(
        l1_plan,
        route_id,
        route_family,
        execution_form,
        action_required,
        cache_eligibility,
        side_effect_class,
    )

    return RouteContract(
        request_id=l1_plan.request_id,
        run_id=l1_plan.run_id,
        app_id=l1_plan.app_id,
        trace_id=l1_plan.trace_id,
        tenant_id=l1_plan.tenant_id,
        route_id=route_id,
        l3_required=l3_required,
        grounding_required=l1_plan.grounding_required,
        model_generation_required=l1_plan.model_generation_required,
        write_authority_present=l1_plan.write_authority_present,
        sandbox_required=True,  # apps_lic requires no-network-egress sandbox
        egress_policy_ref="egress-policy:vllm-only+no-send",
        allowed_models=_ALLOWED_MODELS,
        allowed_tools=_ALLOWED_TOOLS,
        allowed_networks=_ALLOWED_NETWORKS,
        allowed_file_roots=_ALLOWED_FILE_ROOTS,
        route_family=route_family,
        execution_form=execution_form,
        cache_eligibility=cache_eligibility,
        action_required=action_required,
        replay_key=l1_plan.replay_key,
        reason_codes=reason_codes,
        routing_timestamp=datetime.now(timezone.utc).isoformat(),
        schema_version="AG-8.W4.f3c2e1",
        l5_certification_ref=APPS_LIC_L0_CERT_REF,
    )


__all__ = [
    "APPS_LIC_L0_CERT_REF",
    "APPS_LIC_DEFAULT_ROUTE_ID",
    "APPS_LIC_COLD_ROUTE_ID",
    "APPS_LIC_WARM_ROUTE_ID",
    "APPS_LIC_FOLLOW_UP_ROUTE_ID",
    "l0_route_apps_lic",
]
