"""Generic L1PlanContract route policy interpreter.

Reads an app-owned route profile and cache bypass policy to derive:
    - route family (from profile's allowed_route_families and route_selection_conditions)
    - execution form (from profile's execution_form_mapping)
    - L3 required flag (from profile's l3_required_for_families)
    - cache eligibility dict (from profile's cache_bypass_policy_ref)

No app-specific route names, field names, or cache policy values are
hardcoded here. All routing logic is driven by the app-owned profile.

Hard laws inherited from L0:
    - Does NOT retrieve, execute, assemble prompts, or write L4.
    - Does NOT call ChromaDB, embedding models, or any external I/O.
    - Emits exactly ONE route family per call.
"""

from __future__ import annotations

import json
import os
from typing import Optional

from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract


def load_route_profile(profile_path: str) -> dict:
    """Load an app-owned route profile from the given path.

    Path is resolved relative to the workspace root (cwd or project root).
    """
    if not os.path.isabs(profile_path):
        root = _workspace_root()
        profile_path = os.path.join(root, profile_path)
    with open(profile_path, encoding="utf-8") as fh:
        return json.load(fh)


def load_cache_policy(policy_path: str) -> dict:
    """Load an app-owned cache bypass policy from the given path."""
    if not os.path.isabs(policy_path):
        root = _workspace_root()
        policy_path = os.path.join(root, policy_path)
    with open(policy_path, encoding="utf-8") as fh:
        return json.load(fh)


def derive_route_family_from_profile(
    l1_plan: L1PlanContract,
    route_profile: dict,
) -> str:
    """Derive the route family by evaluating profile-defined conditions.

    Evaluation order (matches apps_lic semantic):
    1. Check if request_type is a forbidden briefing-only type → R5 terminal default
    2. Evaluate R4 condition (fresh context) → R4 if satisfied
    3. Evaluate R3R4 condition (research authorized) → R3R4 if satisfied
    4. Default to terminal fallback family

    Returns the matched route family string from allowed_route_families.
    """
    conditions = route_profile.get("route_selection_conditions", {})
    allowed = route_profile.get("allowed_route_families", [])
    forbidden = route_profile.get("forbidden_route_families", [])

    task_spec = l1_plan.task_spec or {}

    # --- Step 1: briefing-only guard (always terminates as fallback) ---
    terminal_defaults = [
        fam for fam, cond in conditions.items()
        if cond.get("is_terminal_default", False)
    ]
    terminal_family = terminal_defaults[0] if terminal_defaults else None

    # Check all families that list briefing-only request types
    for fam, cond in conditions.items():
        briefing_types = cond.get("briefing_only_request_types", [])
        if briefing_types:
            req_field = cond.get("request_type_field", "request_type")
            request_type = str(task_spec.get(req_field, "")).lower()
            for btype in briefing_types:
                if btype.lower() in request_type:
                    # Briefing-only → terminal fallback
                    if terminal_family and terminal_family in allowed:
                        return terminal_family

    # --- Step 2: evaluate each allowed family in order ---
    # R4 (fresh context) check
    for fam in allowed:
        if fam in forbidden:
            continue
        cond = conditions.get(fam, {})
        if cond.get("requires_fresh_context", False):
            if _check_fresh_context(l1_plan, cond):
                return fam

    # R3R4 (research authorized) check
    for fam in allowed:
        if fam in forbidden:
            continue
        cond = conditions.get(fam, {})
        if cond.get("requires_research_authorization", False):
            if _check_research_authorized(task_spec, cond):
                return fam

    # --- Step 3: terminal default fallback ---
    if terminal_family and terminal_family in allowed:
        return terminal_family

    # Safety: return last allowed family
    return allowed[-1] if allowed else "R5_FALLBACK"


def derive_execution_form_from_profile(route_family: str, route_profile: dict) -> str:
    """Derive execution form from profile's execution_form_mapping."""
    mapping = route_profile.get("execution_form_mapping", {})
    return mapping.get(route_family, "TERMINAL_FALLBACK")


def derive_l3_required_from_profile(route_family: str, route_profile: dict) -> bool:
    """Derive l3_required from profile's l3_required_for_families list."""
    l3_families = route_profile.get("l3_required_for_families", [])
    return route_family in l3_families


def derive_cache_eligibility_from_policy(
    route_family: str,
    route_profile: dict,
    cache_policy: Optional[dict] = None,
) -> dict[str, bool]:
    """Derive cache eligibility dict from app-owned cache policy.

    Uses the cache_bypass_policy_ref in the route profile to locate the
    policy (already loaded by the caller as cache_policy).

    Returns a dict with the same keys the tests assert on:
        r1a_exact, r1b_semantic, r3_grounded, r4_action,
        final_draft_r1a_bypass, final_draft_r1b_bypass,
        support_artifacts_cache_allowed
    """
    terminal_families = route_profile.get("terminal_execution_families", [])
    is_fallback = route_family in terminal_families

    # Defaults (conservative bypass)
    r1a_bypassed = True
    r1b_bypassed = True

    if cache_policy:
        r1a_bypassed = cache_policy.get("r1a_exact_cache", {}).get(
            "bypassed_for_final_drafts", True
        )
        r1b_bypassed = cache_policy.get("r1b_semantic_cache", {}).get(
            "bypassed_for_final_drafts", True
        )

    return {
        "r1a_exact": False if r1a_bypassed else (not is_fallback),
        "r1b_semantic": False if r1b_bypassed else (not is_fallback),
        "r3_grounded": not is_fallback,
        "r4_action": False,
        "final_draft_r1a_bypass": r1a_bypassed,
        "final_draft_r1b_bypass": r1b_bypassed,
        "support_artifacts_cache_allowed": not is_fallback,
    }


# ---------------------------------------------------------------------------
# Internal helpers — no apps_lic-specific field names; all come from profile
# ---------------------------------------------------------------------------

def _check_fresh_context(l1_plan: L1PlanContract, cond: dict) -> bool:
    """Return True if fresh valid context exists per condition spec.

    R4 fires when all fresh_context_fields in task_spec are truthy AND,
    if a grounding_context_field is specified, that field is also truthy
    in task_spec. l1_plan.grounding_required is NOT consulted here — it
    indicates whether grounding must occur, not whether context is fresh.
    """
    task_spec = l1_plan.task_spec or {}

    fresh_fields = cond.get("fresh_context_fields", [])
    if not fresh_fields:
        return False

    # All listed fresh-context fields must be truthy
    for field in fresh_fields:
        if not task_spec.get(field, False):
            return False

    # Optionally check a dedicated grounding-context indicator field.
    # If grounding_satisfied_when_not_required=True and plan.grounding_required is
    # False, skip this check (context is considered satisfied without the field).
    grounding_ctx_field = cond.get("grounding_context_field")
    if grounding_ctx_field:
        sat_when_not_required = cond.get("grounding_satisfied_when_not_required", False)
        if sat_when_not_required and not l1_plan.grounding_required:
            pass  # satisfied — skip field check
        elif not task_spec.get(grounding_ctx_field, False):
            return False

    return True


def _check_research_authorized(task_spec: dict, cond: dict) -> bool:
    """Return True if research is authorized per condition spec."""
    allow_field = cond.get("research_allow_field", "allow_research")
    types_field = cond.get("research_types_field", "research_evidence_types")
    disabled_field = cond.get("research_disabled_field", "research_disabled_by_policy")

    if task_spec.get(disabled_field, False):
        return False
    if not task_spec.get(allow_field, False):
        return False
    research_types = task_spec.get(types_field, [])
    return bool(research_types)


def _workspace_root() -> str:
    """Resolve workspace root as the directory containing pyproject.toml or pytest.ini."""
    candidate = os.path.abspath(os.getcwd())
    for _ in range(8):
        if os.path.isfile(os.path.join(candidate, "pyproject.toml")) or \
           os.path.isfile(os.path.join(candidate, "pytest.ini")):
            return candidate
        parent = os.path.dirname(candidate)
        if parent == candidate:
            break
        candidate = parent
    return os.path.abspath(os.getcwd())
