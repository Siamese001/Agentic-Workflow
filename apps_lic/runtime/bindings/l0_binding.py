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
    - execution_form='managed_workflow' for R4 and R3R4; 'terminal_fallback' for R5
      (canonical casing emitted by l0_route_apps_lic regardless of profile map casing).
    - Cache bypass for final drafts: R1A exact and R1B semantic always bypassed.
    - Briefing-only requests route to apps_research directly, never through apps_lic L0.

Plan: .windsurf/plans/apps-lic-u0-runtime-package-complete-f8e2a1.md (W2)
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.contracts.route_contract import RouteContract
from agentic_core.L0_routing.generic_route_policy_interpreter import (
    load_route_profile,
    load_cache_policy,
    derive_route_family_from_profile,
    derive_execution_form_from_profile,
    derive_l3_required_from_profile,
    derive_cache_eligibility_from_policy,
    _check_fresh_context,
    _check_research_authorized,
)


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

# Canonical RouteContract.execution_form values (L3/L2 bindings consume these).
_EXECUTION_FORM_MANAGED: str = "managed_workflow"
_EXECUTION_FORM_TERMINAL: str = "terminal_fallback"

# Stable aliases used by W4 tests (map to canonical R4/R3R4/R5 model)
APPS_LIC_DEFAULT_ROUTE_ID: str = ROUTE_ID_R4_DEFAULT
APPS_LIC_COLD_ROUTE_ID: str = ROUTE_ID_R3R4_WITH_RESEARCH
APPS_LIC_WARM_ROUTE_ID: str = ROUTE_ID_R4_DEFAULT
APPS_LIC_FOLLOW_UP_ROUTE_ID: str = ROUTE_ID_R3R4_WITH_RESEARCH

_ROUTE_PROFILE_RELPATH: str = (
    "apps_lic/config/domain_contract/l0_route_profile.outreach_message.v1.json"
)
_CACHE_POLICY_RELPATH: str = (
    "apps_lic/config/domain_contract/final_draft_cache_policy.outreach_message.v1.json"
)

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

# ---------------------------------------------------------------------------
# Lazy profile singletons — loaded once from app-owned JSON files
# ---------------------------------------------------------------------------
_route_profile: dict | None = None
_cache_policy: dict | None = None


def _get_route_profile() -> dict:
    global _route_profile
    if _route_profile is None:
        _route_profile = load_route_profile(_ROUTE_PROFILE_RELPATH)
    return _route_profile


def _get_cache_policy() -> dict:
    global _cache_policy
    if _cache_policy is None:
        _cache_policy = load_cache_policy(_CACHE_POLICY_RELPATH)
    return _cache_policy


# ---------------------------------------------------------------------------
# Thin-adapter public helpers (preserve public API for tests)
# ---------------------------------------------------------------------------

def _derive_route_family(l1_plan: L1PlanContract) -> str:
    """Thin adapter: delegates to generic route policy interpreter using apps_lic profile."""
    return derive_route_family_from_profile(l1_plan, _get_route_profile())


def _has_fresh_valid_context(l1_plan: L1PlanContract) -> bool:
    """Thin adapter: delegates to generic fresh-context check using profile conditions."""
    profile = _get_route_profile()
    cond = profile.get("route_selection_conditions", {}).get(
        ROUTE_FAMILY_R4_MANAGED_DRAFT, {}
    )
    return _check_fresh_context(l1_plan, cond)


def _is_research_authorized(l1_plan: L1PlanContract) -> bool:
    """Thin adapter: delegates to generic research-authorization check using profile conditions."""
    profile = _get_route_profile()
    cond = profile.get("route_selection_conditions", {}).get(
        ROUTE_FAMILY_R3R4_MANAGED_RESEARCH_THEN_DRAFT, {}
    )
    return _check_research_authorized(l1_plan.task_spec or {}, cond)


def _derive_route_id(l1_plan: L1PlanContract, route_family: str) -> str:
    """Select route_id based on route_family — thin mapping, no app logic in core.

    R4 -> ROUTE_ID_R4_DEFAULT (HOP draft workflow)
    R3R4 -> ROUTE_ID_R3R4_WITH_RESEARCH (apps_research support then HOP)
    R5 -> ROUTE_ID_R5_FALLBACK (terminal fallback, no draft)
    """
    _route_id_map = {
        ROUTE_FAMILY_R4_MANAGED_DRAFT: ROUTE_ID_R4_DEFAULT,
        ROUTE_FAMILY_R3R4_MANAGED_RESEARCH_THEN_DRAFT: ROUTE_ID_R3R4_WITH_RESEARCH,
        ROUTE_FAMILY_R5_FALLBACK: ROUTE_ID_R5_FALLBACK,
    }
    return _route_id_map.get(route_family, ROUTE_ID_R5_FALLBACK)


def _derive_execution_form(route_family: str) -> str:
    """Thin adapter: derives canonical execution form from apps_lic route profile."""
    profile_form = derive_execution_form_from_profile(route_family, _get_route_profile())
    return _canonicalize_execution_form(profile_form)


def _canonicalize_execution_form(profile_execution_form: str) -> str:
    """Map profile execution_form_mapping values to canonical RouteContract casing."""
    normalized = profile_execution_form.strip().upper().replace("-", "_")
    if normalized == "MANAGED_WORKFLOW":
        return _EXECUTION_FORM_MANAGED
    if normalized == "TERMINAL_FALLBACK":
        return _EXECUTION_FORM_TERMINAL
    return profile_execution_form.strip().lower()


def _derive_l3_required(route_family: str) -> bool:
    """Thin adapter: derives l3_required from apps_lic route profile."""
    return derive_l3_required_from_profile(route_family, _get_route_profile())


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
    """Thin adapter: derives cache eligibility from apps_lic cache policy profile."""
    return derive_cache_eligibility_from_policy(
        route_family, _get_route_profile(), _get_cache_policy()
    )


def _derive_side_effect_class(l1_plan: L1PlanContract) -> str:
    """Verified from task_spec; always read_only for outreach generation."""
    return str(l1_plan.task_spec.get("side_effect_class", "read_only"))


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
    """Thin adapter: emit a single deterministic RouteContract from an apps_lic L1 plan.

    Delegates all route/cache/execution policy decisions to the generic
    route policy interpreter, driven by app-owned profile files.

    Args:
        l1_plan: L1PlanContract output of l1_plan_apps_lic.

    Returns:
        RouteContract with route_id, execution_form, l3_required, grounding flags,
        capability surface, side_effect_class, cache_eligibility, and reason_codes.

    Raises:
        TypeError: if l1_plan is not an L1PlanContract.
        ValueError: if l1_plan.app_id != 'apps_lic'.
        ValueError: if execution_form violates FINAL L0 MODEL hard law.
    """
    if not isinstance(l1_plan, L1PlanContract):
        raise TypeError(
            f"l0_route_apps_lic expected L1PlanContract, got {type(l1_plan).__name__}"
        )
    if l1_plan.app_id != "apps_lic":
        raise ValueError(
            f"l0_route_apps_lic expected app_id='apps_lic'; got {l1_plan.app_id!r}"
        )

    # FINAL L0 MODEL: all policy derived from app-owned profiles via generic interpreter
    route_family = _derive_route_family(l1_plan)
    route_id = _derive_route_id(l1_plan, route_family)
    execution_form = _derive_execution_form(route_family)
    l3_required = _derive_l3_required(route_family)
    action_required = _derive_action_required(l1_plan)
    cache_eligibility = _derive_cache_eligibility(route_family)
    side_effect_class = _derive_side_effect_class(l1_plan)

    # FINAL L0 MODEL hard law: R4 and R3R4 must produce managed_workflow; R5 terminal_fallback.
    if route_family in (ROUTE_FAMILY_R4_MANAGED_DRAFT, ROUTE_FAMILY_R3R4_MANAGED_RESEARCH_THEN_DRAFT):
        if execution_form != _EXECUTION_FORM_MANAGED:
            raise ValueError(
                f"l0_route_apps_lic: route_family={route_family} but execution_form "
                f"derived as {execution_form!r} — FINAL L0 MODEL hard law violated"
            )
    elif route_family == ROUTE_FAMILY_R5_FALLBACK:
        if execution_form != _EXECUTION_FORM_TERMINAL:
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
