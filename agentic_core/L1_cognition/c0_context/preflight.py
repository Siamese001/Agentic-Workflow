"""C0.0 grounding eligibility + C0.1 retrieval plan builder.

Spec: ``docs/reference/03_L0_Routing/C0 - Retrieval/C0 Context Engine.md``
"""

from __future__ import annotations

from agentic_core.L1_cognition.c0_context.types import (
    BOUND_PARAMS,
    RETRIEVAL_MODES,
    SOURCE_CLASSES,
    C0PreflightStatus,
    RetrievalPlan,
    RouteContractView,
    SupportTarget,
)

# Minimum tokens required to run at least one bounded retrieval pass.
MIN_BUDGET_FLOOR_TOKENS: int = 512


def preflight(route: RouteContractView) -> C0PreflightStatus:
    """C0.0 — decide whether C0 should run for this route.

    Checks (per spec):
      - grounding_required == true
      - RouteContract allows C0 retrieval (route_id implies grounded path)
      - source classes are approved for this tenant + route
      - no blocked data class is requested
      - budget is sufficient for at least one bounded retrieval pass
    """
    if not route.grounding_required:
        return C0PreflightStatus(
            eligible=False,
            blocked_reason="grounding_not_required",
            allowed_source_classes=frozenset(),
            evidence_standard="none",
            budget_floor_tokens=0,
        )
    if route.route_id not in {"R3_GROUNDED", "R3_SIMPLE_GROUNDED_READ", "R3R4_MANAGED_WORKFLOW"}:
        return C0PreflightStatus(
            eligible=False,
            blocked_reason=f"route {route.route_id} does not allow C0 retrieval",
            allowed_source_classes=frozenset(),
            evidence_standard="none",
            budget_floor_tokens=0,
        )
    # Approved source classes — intersection of route allowed + global vocabulary.
    allowed = (route.allowed_sources & SOURCE_CLASSES) - route.disallowed_sources
    if not allowed:
        return C0PreflightStatus(
            eligible=False,
            blocked_reason="no allowed source class after applying disallowed list",
            allowed_source_classes=frozenset(),
            evidence_standard="none",
            budget_floor_tokens=0,
        )
    if route.data_class in {"restricted", "blocked"}:
        return C0PreflightStatus(
            eligible=False,
            blocked_reason=f"data_class={route.data_class!r} blocked",
            allowed_source_classes=frozenset(),
            evidence_standard="none",
            budget_floor_tokens=0,
        )
    if route.token_budget < MIN_BUDGET_FLOOR_TOKENS:
        return C0PreflightStatus(
            eligible=False,
            blocked_reason=f"token_budget={route.token_budget} < floor={MIN_BUDGET_FLOOR_TOKENS}",
            allowed_source_classes=frozenset(),
            evidence_standard="none",
            budget_floor_tokens=MIN_BUDGET_FLOOR_TOKENS,
        )
    # Strict standard for high-stakes support targets.
    high_stakes = route.support_target in {
        SupportTarget.POLICY_CLAUSE,
        SupportTarget.INCIDENT_EVIDENCE,
        SupportTarget.ROOT_CAUSE_RANKING,
        SupportTarget.CODE_LOCATION,
    }
    return C0PreflightStatus(
        eligible=True,
        blocked_reason="",
        allowed_source_classes=allowed,
        evidence_standard="strict" if high_stakes else "default",
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
    "build_retrieval_plan",
    "preflight",
]
