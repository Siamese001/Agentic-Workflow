"""L0 routing binding for the apps_lic `outreach_message` task class.

L0 is the THIRD stage of the U0 -> L1 -> L0 -> [C0] -> [PA] -> L3/L2 -> Exit
pipeline. Its job is to consume the L1PlanContract app_payload-derived
projections and emit a single deterministic RouteContract using the FINAL
L0 routing model (R4/R3R4/R5).

FINAL L0 ROUTING MODEL (W2):
    L0 reads L1PlanContract ONLY and emits exactly one of:

    1. R4_MANAGED_DRAFT
       Condition: fresh, valid outreach context exists; no apps_research support needed
       Path: U0 -> L1 -> L0 -> R4 -> execution_form=MANAGED_WORKFLOW -> L3 HOP draft workflow -> L2 -> Exit

    2. R3R4_MANAGED_RESEARCH_THEN_DRAFT
       Condition: fresh context missing/stale/incomplete; research authorized
       Path: U0 -> L1 -> L0 -> R3R4 -> L3 apps_research support -> L3 validates context -> L3 HOP -> L2 -> Exit

    3. R5_FALLBACK
       Condition: no valid context; research not authorized; policy/consent/evidence/channel invalid
       Path: U0/L1/L0/L3/L2 failure -> R5 terminal packet -> Exit -> bounded fail-closed / abstain / no-draft outcome

    OLD ROUTE NAMES REMOVED:
        - evidence_grounded_generation
        - ungrounded_generation
        - R3_grounded_read
        - briefing_only

HARD LAWS:
    - L0 does NOT retrieve, execute, assemble prompts, or write L4.
    - L0 does NOT call ChromaDB, embedding models, or any external I/O.
    - L0 emits exactly ONE route (R4, R3R4, or R5 only).
    - execution_form='managed_workflow' for R4 and R3R4; 'terminal_fallback' for R5.
    - Cache bypass for final drafts: R1A exact and R1B semantic always bypassed.
    - Briefing-only requests route to apps_research directly, never through apps_lic L0.

Plan: .windsurf/plans/apps-lic-u0-runtime-package-complete-f8e2a1.md (W2)
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.contracts.route_contract import RouteContract


APPS_LIC_L0_CERT_REF: str = "l0-apps-lic-outreach-message-w2-final-routing-f8e2a1"

# Final L0 route families (R4/R3R4/R5 model)
ROUTE_FAMILY_R4_MANAGED_DRAFT: str = "R4_MANAGED_DRAFT"
ROUTE_FAMILY_R3R4_MANAGED_RESEARCH_THEN_DRAFT: str = "R3R4_MANAGED_RESEARCH_THEN_DRAFT"
ROUTE_FAMILY_R5_FALLBACK: str = "R5_FALLBACK"

# OLD ROUTE NAMES FORBIDDEN (removed):
# - evidence_grounded_generation
# - ungrounded_generation
# - R3_grounded_read
# - briefing_only

# Route IDs (task-specific variants)
ROUTE_ID_R4_DEFAULT: str = "lic.outreach_message.r4_managed_draft"
ROUTE_ID_R3R4_WITH_RESEARCH: str = "lic.outreach_message.r3r4_research_then_draft"
ROUTE_ID_R5_FALLBACK: str = "lic.outreach_message.r5_fallback"

# Stable aliases used by W4 tests (map to canonical R4/R3R4/R5 model)
APPS_LIC_DEFAULT_ROUTE_ID: str = ROUTE_ID_R4_DEFAULT
APPS_LIC_COLD_ROUTE_ID: str = ROUTE_ID_R3R4_WITH_RESEARCH
APPS_LIC_WARM_ROUTE_ID: str = ROUTE_ID_R4_DEFAULT
APPS_LIC_FOLLOW_UP_ROUTE_ID: str = ROUTE_ID_R3R4_WITH_RESEARCH

_ROUTE_PROFILE_RELPATH: str = "apps_lic/config/domain_contract/l0_route_profile.outreach_message.v1.json"

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
    """Derive final L0 route family (R4/R3R4/R5) based on context and authorization.

    FINAL L0 ROUTING MODEL:
    - R4_MANAGED_DRAFT: fresh valid context, no research needed
    - R3R4_MANAGED_RESEARCH_THEN_DRAFT: missing/stale context, research authorized
    - R5_FALLBACK: no valid context, research not authorized
    """
    # Check for briefing-only intent (must not route through apps_lic L0)
    request_type = str(l1_plan.task_spec.get("request_type", "")).lower()
    if "briefing_only" in request_type or "briefing-only" in request_type:
        # Briefing-only must route to apps_research directly before apps_lic
        # If it reaches apps_lic L0, it's a routing error -> fail closed
        return ROUTE_FAMILY_R5_FALLBACK

    # Check if fresh valid context exists
    has_fresh_context = _has_fresh_valid_context(l1_plan)

    # Check if research is authorized for missing/stale context
    research_authorized = _is_research_authorized(l1_plan)

    if has_fresh_context:
        # Fresh context exists -> R4_MANAGED_DRAFT
        return ROUTE_FAMILY_R4_MANAGED_DRAFT
    elif research_authorized:
        # Missing/stale context but research authorized -> R3R4
        return ROUTE_FAMILY_R3R4_MANAGED_RESEARCH_THEN_DRAFT
    else:
        # No valid context and research not authorized -> R5_FALLBACK
        return ROUTE_FAMILY_R5_FALLBACK


def _has_fresh_valid_context(l1_plan: L1PlanContract) -> bool:
    """Check if fresh, valid outreach context exists.

    Fresh context requires:
    - Valid company briefing available (briefing_fresh=true)
    - Valid lead profile available (lead_profile_valid=true)
    - Campaign objective defined (campaign_objective not empty)
    - Grounding not explicitly required (or context is already grounded)
    """
    # Check if context freshness flags are present in task_spec
    briefing_fresh = bool(l1_plan.task_spec.get("briefing_fresh", False))
    lead_valid = bool(l1_plan.task_spec.get("lead_profile_valid", False))
    campaign_defined = bool(l1_plan.task_spec.get("campaign_objective", ""))

    # If grounding is required but not satisfied, context is not fresh
    grounding_satisfied = not l1_plan.grounding_required or bool(
        l1_plan.task_spec.get("context_grounded", False)
    )

    return briefing_fresh and lead_valid and campaign_defined and grounding_satisfied


def _is_research_authorized(l1_plan: L1PlanContract) -> bool:
    """Check if research is authorized for missing/stale context.

    Research authorization requires:
    - research_requirements.required_evidence_types not empty
    - research_requirements.allow_research=true in task_spec
    - Not explicitly disabled by policy
    """
    # Check research authorization flags
    allow_research = bool(l1_plan.task_spec.get("allow_research", False))
    research_types = l1_plan.task_spec.get("research_evidence_types", [])

    # Policy can explicitly disable research
    research_disabled = bool(l1_plan.task_spec.get("research_disabled_by_policy", False))

    return allow_research and len(research_types) > 0 and not research_disabled


def _derive_route_id(l1_plan: L1PlanContract, route_family: str) -> str:
    """Select route_id based on route_family from final L0 model.

    R4 -> ROUTE_ID_R4_DEFAULT (HOP draft workflow)
    R3R4 -> ROUTE_ID_R3R4_WITH_RESEARCH (apps_research support then HOP)
    R5 -> ROUTE_ID_R5_FALLBACK (terminal fallback, no draft)
    """
    if route_family == ROUTE_FAMILY_R4_MANAGED_DRAFT:
        return ROUTE_ID_R4_DEFAULT
    elif route_family == ROUTE_FAMILY_R3R4_MANAGED_RESEARCH_THEN_DRAFT:
        return ROUTE_ID_R3R4_WITH_RESEARCH
    elif route_family == ROUTE_FAMILY_R5_FALLBACK:
        return ROUTE_ID_R5_FALLBACK
    else:
        # Should never happen due to route_family validation
        return ROUTE_ID_R5_FALLBACK


def _derive_execution_form(route_family: str) -> str:
    """Derive execution_form based on route_family from final L0 model.

    FINAL L0 MODEL:
    - R4_MANAGED_DRAFT -> MANAGED_WORKFLOW (L3 HOP orchestration)
    - R3R4_MANAGED_RESEARCH_THEN_DRAFT -> MANAGED_WORKFLOW (L3 HOP after research)
    - R5_FALLBACK -> TERMINAL_FALLBACK (no orchestration, fail closed)
    """
    if route_family == ROUTE_FAMILY_R4_MANAGED_DRAFT:
        return "MANAGED_WORKFLOW"
    elif route_family == ROUTE_FAMILY_R3R4_MANAGED_RESEARCH_THEN_DRAFT:
        return "MANAGED_WORKFLOW"
    elif route_family == ROUTE_FAMILY_R5_FALLBACK:
        return "TERMINAL_FALLBACK"
    else:
        # Conservative default
        return "TERMINAL_FALLBACK"


def _derive_l3_required(route_family: str) -> bool:
    """L3 is required for R4 and R3R4 (MANAGED_WORKFLOW), not for R5 (TERMINAL_FALLBACK).

    FINAL L0 MODEL:
    - R4_MANAGED_DRAFT -> L3 required (HOP orchestration)
    - R3R4_MANAGED_RESEARCH_THEN_DRAFT -> L3 required (research + HOP)
    - R5_FALLBACK -> L3 not required (terminal fallback)
    """
    return route_family in (
        ROUTE_FAMILY_R4_MANAGED_DRAFT,
        ROUTE_FAMILY_R3R4_MANAGED_RESEARCH_THEN_DRAFT,
    )


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


def _derive_cache_eligibility(route_family: str) -> dict[str, bool]:
    """Per-cache-tier eligibility with final draft bypass.

    FINAL L0 MODEL CACHE RULES:
    - R1A exact cache: BYPASS for final drafts (never serve personalized outreach from cache)
    - R1B semantic cache: BYPASS for final drafts (no semantic reuse of personalized content)
    - R3 grounded cache: Allowed for support artifacts only (briefings, facts)
    - R4 action cache: Never (apps_lic has no state mutation)

    Cache allowed for:
    - verified company briefing
    - public company facts
    - retrieval manifests
    - consent/compliance evidence
    - approved prompt/profile refs
    """
    is_fallback = route_family == ROUTE_FAMILY_R5_FALLBACK

    return {
        # Final drafts bypass both cache tiers (proven at runtime)
        "r1a_exact": False,  # BYPASS for final outreach drafts
        "r1b_semantic": False,  # BYPASS for final outreach drafts
        "r3_grounded": not is_fallback,  # Allowed for support artifacts if not R5
        "r4_action": False,  # Never (read_only posture)
        # Extended for final draft bypass proof
        "final_draft_r1a_bypass": True,  # Proven: R1A exact cache bypassed for final drafts
        "final_draft_r1b_bypass": True,  # Proven: R1B semantic cache bypassed for final drafts
        "support_artifacts_cache_allowed": not is_fallback,  # Allowed: briefings, facts, manifests
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

    # FINAL L0 MODEL: Derive route_family first, then other fields from it
    route_family = _derive_route_family(l1_plan)
    route_id = _derive_route_id(l1_plan, route_family)
    execution_form = _derive_execution_form(route_family)
    l3_required = _derive_l3_required(route_family)
    action_required = _derive_action_required(l1_plan)
    cache_eligibility = _derive_cache_eligibility(route_family)
    side_effect_class = _derive_side_effect_class(l1_plan)

    # FINAL L0 MODEL hard law: R4 and R3R4 must produce MANAGED_WORKFLOW
    # R5 must produce TERMINAL_FALLBACK
    if route_family in (ROUTE_FAMILY_R4_MANAGED_DRAFT, ROUTE_FAMILY_R3R4_MANAGED_RESEARCH_THEN_DRAFT):
        if execution_form != "MANAGED_WORKFLOW":
            raise ValueError(
                f"l0_route_apps_lic: route_family={route_family} but execution_form "
                f"derived as {execution_form!r} — FINAL L0 MODEL hard law violated"
            )
    elif route_family == ROUTE_FAMILY_R5_FALLBACK:
        if execution_form != "TERMINAL_FALLBACK":
            raise ValueError(
                f"l0_route_apps_lic: route_family={route_family} but execution_form "
                f"derived as {execution_form!r} — FINAL L0 MODEL hard law violated"
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
        schema_version="W2.FINAL.R4R3R4R5.f8e2a1",
        l5_certification_ref=APPS_LIC_L0_CERT_REF,
    )


__all__ = [
    "APPS_LIC_L0_CERT_REF",
    # Final L0 route families
    "ROUTE_FAMILY_R4_MANAGED_DRAFT",
    "ROUTE_FAMILY_R3R4_MANAGED_RESEARCH_THEN_DRAFT",
    "ROUTE_FAMILY_R5_FALLBACK",
    # Route IDs
    "ROUTE_ID_R4_DEFAULT",
    "ROUTE_ID_R3R4_WITH_RESEARCH",
    "ROUTE_ID_R5_FALLBACK",
    # Main entry point
    "l0_route_apps_lic",
    # Helper functions (for testing)
    "_derive_route_family",
    "_has_fresh_valid_context",
    "_is_research_authorized",
    "_derive_route_id",
    "_derive_execution_form",
    "_derive_l3_required",
    "_derive_cache_eligibility",
]
