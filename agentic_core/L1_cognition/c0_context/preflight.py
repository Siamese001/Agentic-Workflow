"""C0.0 advisory grounding analysis + C0.1 retrieval plan builder.

W2 c0-policy-rectification-f7b2a9: L1 preflight is now advisory only.
L0 is the authority that freezes C0 policy into RouteContract.c0_policy.

Spec: ``docs/reference/03_L0_Routing/C0 - Retrieval/C0 Context Engine.md``
"""

from __future__ import annotations

import warnings

from agentic_core.L1_cognition.c0_context.types import (
    BOUND_PARAMS,
    L1C0Advisory,
    RETRIEVAL_MODES,
    SOURCE_CLASSES,
    C0PreflightStatus,
    RetrievalPlan,
    RouteContractView,
    SupportTarget,
)

# Minimum tokens required to run at least one bounded retrieval pass.
MIN_BUDGET_FLOOR_TOKENS: int = 512


def analyze_grounding_advisory(
    task_spec: str,
    query_spec: str,
    *,
    support_expectation: str = "",
    confidence: float = 0.85,
) -> L1C0Advisory:
    """W2 — L1 advisory grounding analysis (does NOT authorize C0 runtime).

    L1 may declare semantic grounding need, but L0 freezes the authoritative
    C0 policy into RouteContract.c0_policy. This function emits advisory
    signals only; it does not decide whether C0 may run.

    Args:
        task_spec: The task description from the user.
        query_spec: The specific query to ground.
        support_expectation: What kind of support is expected.
        confidence: L1 confidence in the assessment.

    Returns:
        L1C0Advisory with advisory fields only.
    """
    # Determine if grounding is needed based on task/query semantics.
    task_lower = task_spec.lower()
    query_lower = query_spec.lower()

    # Grounding signals in task/query text.
    asks_factual = any(t in task_lower or query_lower for t in (
        "what", "which", "who", "when", "where", "explain", "summarize",
        "according to", "reference", "source", "cite", "document",
    ))
    asks_policy = any(t in task_lower or query_lower for t in (
        "policy", "rule", "clause", "compliance", "violation", "standard",
    ))
    asks_code = any(t in task_lower or query_lower for t in (
        "code", "function", "class", "module", "api", "endpoint",
    ))
    asks_incident = any(t in task_lower or query_lower for t in (
        "incident", "outage", "error", "exception", "bug", "failure",
    ))

    # Determine support target from query semantics.
    if asks_policy:
        support_target = SupportTarget.POLICY_CLAUSE
    elif asks_code:
        support_target = SupportTarget.CODE_LOCATION
    elif asks_incident:
        support_target = SupportTarget.INCIDENT_EVIDENCE
    elif asks_factual:
        support_target = SupportTarget.SOURCE_SUMMARY
    else:
        support_target = SupportTarget.SOURCE_SUMMARY

    # Grounding is required for factual/policy/code/incident queries.
    grounding_required = asks_factual or asks_policy or asks_code or asks_incident

    # Build reason codes for traceability.
    reason_codes: list[str] = []
    if grounding_required:
        if asks_factual:
            reason_codes.append("l1:factual_query")
        if asks_policy:
            reason_codes.append("l1:policy_reference")
        if asks_code:
            reason_codes.append("l1:code_reference")
        if asks_incident:
            reason_codes.append("l1:incident_evidence")
    else:
        reason_codes.append("l1:no_grounding_signals")

    return L1C0Advisory(
        grounding_required=grounding_required,
        support_expectation=support_expectation or support_target.value,
        support_target=support_target,
        grounding_reason_codes=tuple(reason_codes),
        confidence=confidence,
    )


def preflight(route: RouteContractView) -> C0PreflightStatus:
    """DEPRECATED: Use analyze_grounding_advisory for L1 advisory.

    C0.0 runtime eligibility checks have moved to L0/C0. L0 now freezes
    C0 policy into RouteContract.c0_policy; C0 preflight reads that.

    This function is kept temporarily for backward compatibility but
    will be removed. It no longer makes authoritative decisions.

    W2 c0-policy-rectification-f7b2a9.
    """
    warnings.warn(
        "preflight() is deprecated. "
        "Use analyze_grounding_advisory() for L1 advisory. "
        "C0 runtime decisions now use RouteContract.c0_policy.",
        DeprecationWarning,
        stacklevel=2,
    )

    # W2: Delegate to new advisory function, then map to legacy C0PreflightStatus.
    # This is a compatibility shim; real C0 decisions now come from L0 policy.
    advisory = analyze_grounding_advisory(
        task_spec=route.route_id,  # Minimal shim - task not available here
        query_spec="",
        support_expectation=route.support_target.value,
    )

    # W2: Do NOT whitelist route IDs here. L0 policy construction decides.
    # This is advisory-only; the real decision is in RouteContract.c0_policy.
    allowed = (route.allowed_sources & SOURCE_CLASSES) - route.disallowed_sources

    # W2: Return advisory status (not authoritative eligibility).
    # C0.0 in L0/C0 now uses RouteContract.c0_policy for runtime decisions.
    return C0PreflightStatus(
        eligible=advisory.grounding_required,  # Advisory only
        blocked_reason="" if advisory.grounding_required else "advisory:grounding_not_required",
        allowed_source_classes=allowed if advisory.grounding_required else frozenset(),
        evidence_standard="advisory",
        budget_floor_tokens=MIN_BUDGET_FLOOR_TOKENS if advisory.grounding_required else 0,
    )


def build_retrieval_plan(
    route: RouteContractView,
    preflight_status: C0PreflightStatus,
    *,
    retrieval_modes: frozenset[str] | None = None,
    cache_policy: str = "READ_THROUGH",
    weak_support_policy: str = "caveat",
) -> RetrievalPlan:
    """C0.1 — convert L1/L0 intent into a bounded search plan.

    Raises:
        ValueError: When preflight_status.eligible is False, when retrieval_modes
            contains an unknown mode, or when bounds violate basic sanity.
    """
    if not preflight_status.eligible:
        raise ValueError(
            f"cannot build retrieval plan; preflight blocked: "
            f"{preflight_status.blocked_reason}",
        )
    modes = (
        retrieval_modes
        if retrieval_modes is not None
        else frozenset({"dense", "sparse", "metadata"})
    )
    unknown = modes - RETRIEVAL_MODES
    if unknown:
        raise ValueError(f"unknown retrieval_modes: {sorted(unknown)}")
    bounds: dict[str, int] = {
        "max_k": route.max_k,
        "max_parent_expansion": route.max_parent_expansion,
        # Default child expansion to parent-expansion budget when absent.
        "max_child_expansion": route.max_parent_expansion,
        "max_graph_hops": route.max_hops,
        "max_refine_attempts": route.max_refine_attempts,
        "max_token_context": route.token_budget,
        "max_source_classes": len(preflight_status.allowed_source_classes),
        "max_latency_ms": route.max_latency_ms,
        "max_cost_tier": 1,
    }
    # Sanity — every BOUND_PARAM listed in spec is populated.
    missing = set(BOUND_PARAMS) - set(bounds.keys())
    if missing:
        raise ValueError(f"retrieval plan missing bound params: {sorted(missing)}")
    return RetrievalPlan(
        source_classes=preflight_status.allowed_source_classes,
        allowed_sources=route.allowed_sources & preflight_status.allowed_source_classes,
        disallowed_sources=route.disallowed_sources,
        retrieval_modes=modes,
        support_target=route.support_target,
        freshness_rule=route.freshness_class,
        evidence_standard=preflight_status.evidence_standard,
        bounds=bounds,
        cache_policy=cache_policy,
        weak_support_policy=weak_support_policy,
        replay_metadata={
            "route_replay_key": route.route_replay_key,
            "policy_hash": route.policy_hash,
            "blueprint_hash": route.blueprint_hash,
        },
    )


__all__ = [
    "MIN_BUDGET_FLOOR_TOKENS",
    "analyze_grounding_advisory",  # W2: new advisory-only function
    "build_retrieval_plan",
    "preflight",  # W2: deprecated, kept for backward compatibility
]
