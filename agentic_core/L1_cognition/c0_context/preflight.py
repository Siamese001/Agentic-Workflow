"""C0.0 advisory grounding analysis + C0.1 retrieval plan builder.

W2 c0-policy-rectification-f7b2a9: Deprecated preflight() removed.
- analyze_grounding_advisory: L1 advisory-only function
- build_retrieval_plan: L1 retrieval planning (for use by L0/C0)

C0 runtime decisions now use RouteContract.c0_policy frozen by L0.
L0 is the authority; L1 provides only advisory signals.

Spec: ``docs/reference/03_L0_Routing/C0 - Retrieval/C0 Context Engine.md``
"""

from __future__ import annotations

from agentic_core.L1_cognition.c0_context.types import (
    BOUND_PARAMS,
    L1C0Advisory,
    RETRIEVAL_MODES,
    SOURCE_CLASSES,
    SupportTarget,
    # W2: Removed preflight, but build_retrieval_plan still needs these
    C0PreflightStatus,
    RetrievalPlan,
    RouteContractView,
)

# Minimum tokens required to run at least one bounded retrieval pass.
MIN_BUDGET_FLOOR_TOKENS: int = 512

_HIGH_STAKES_TARGETS: frozenset[SupportTarget] = frozenset({
    SupportTarget.POLICY_CLAUSE,
    SupportTarget.INCIDENT_EVIDENCE,
    SupportTarget.ROOT_CAUSE_RANKING,
    SupportTarget.CODE_LOCATION,
})


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
    """Compatibility eligibility check for callers that still need C0.0 status.

    L0 remains the authority for runtime C0 policy. This helper only derives the
    bounded retrieval status expected by older C0 tests and plan builders.
    """
    if not route.grounding_required:
        return C0PreflightStatus(
            eligible=False,
            blocked_reason="grounding_not_required",
            allowed_source_classes=frozenset(),
            evidence_standard="none",
            budget_floor_tokens=0,
        )

    if not route.route_id.startswith("R3"):
        return C0PreflightStatus(
            eligible=False,
            blocked_reason=f"route_id {route.route_id} does not allow C0 retrieval",
            allowed_source_classes=frozenset(),
            evidence_standard="none",
            budget_floor_tokens=0,
        )

    allowed = (route.allowed_sources & SOURCE_CLASSES) - route.disallowed_sources
    if not allowed:
        return C0PreflightStatus(
            eligible=False,
            blocked_reason="no allowed source class remains after disallowed sources",
            allowed_source_classes=frozenset(),
            evidence_standard="none",
            budget_floor_tokens=0,
        )

    if route.data_class in {"blocked", "restricted"}:
        return C0PreflightStatus(
            eligible=False,
            blocked_reason=f"data_class {route.data_class} is not eligible for C0 retrieval",
            allowed_source_classes=frozenset(),
            evidence_standard="none",
            budget_floor_tokens=0,
        )

    if route.token_budget < MIN_BUDGET_FLOOR_TOKENS:
        return C0PreflightStatus(
            eligible=False,
            blocked_reason=(
                f"token_budget {route.token_budget} below C0 floor "
                f"{MIN_BUDGET_FLOOR_TOKENS}"
            ),
            allowed_source_classes=frozenset(),
            evidence_standard="none",
            budget_floor_tokens=0,
        )

    evidence_standard = "strict" if route.support_target in _HIGH_STAKES_TARGETS else "default"
    return C0PreflightStatus(
        eligible=True,
        blocked_reason="",
        allowed_source_classes=frozenset(allowed),
        evidence_standard=evidence_standard,
        budget_floor_tokens=MIN_BUDGET_FLOOR_TOKENS,
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
    "analyze_grounding_advisory",  # W2: L1 advisory-only (replaces deprecated preflight)
    "preflight",
    "build_retrieval_plan",
]
