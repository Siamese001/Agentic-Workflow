"""v12 §7 — Cold-Start Safeguard.

When the classifier is not confident (``confidence <
cold_start_conservative_threshold``), the dispatcher overrides the top-pick
route to ``R3_GROUNDED`` at ``TIER_M`` and appends the original top-pick to
the fallback_chain. Pure function — no state, safe to call per-request.

Rationale (v12 §7 / Tian Pan 2025):
  *"The cost of unnecessarily routing to a mid-tier model is much lower than
  the cost of a bad answer from a small model that should have been
  escalated."*
"""

from __future__ import annotations

from dataclasses import dataclass

from agentic_core.L0_routing.types.route_contract_v12_extensions import (
    CostTier,
    FallbackEntry,
    RouteId,
)


@dataclass(frozen=True)
class ColdStartDecision:
    """Output of ``maybe_override_for_cold_start``.

    Attributes
    ----------
    overridden:
        True iff the top-pick was replaced with a conservative route.
    route_id:
        The route to actually dispatch (original top-pick or overridden).
    cost_tier:
        The cost tier to use.
    fallback_chain_prefix:
        Entries to prepend to the route's default fallback_chain. Non-empty
        iff ``overridden`` is True (contains the original top-pick so
        downstream retry can try it).
    reason_codes:
        Reason codes to append to the Route Contract.
    """

    overridden: bool
    route_id: RouteId
    cost_tier: CostTier
    fallback_chain_prefix: tuple[FallbackEntry, ...]
    reason_codes: tuple[str, ...]


def maybe_override_for_cold_start(
    top_pick: RouteId,
    top_pick_tier: CostTier,
    classifier_confidence: float,
    cold_start_threshold: float,
    *,
    conservative_route: RouteId = RouteId.R3_GROUNDED,
    conservative_tier: CostTier = CostTier.TIER_M,
) -> ColdStartDecision:
    """Apply v12 §7 cold-start override if classifier confidence is too low.

    Parameters
    ----------
    top_pick:
        The dispatcher's highest-scoring route candidate.
    top_pick_tier:
        Cost tier the dispatcher assigned to the top pick.
    classifier_confidence:
        Classifier probability in [0, 1].
    cold_start_threshold:
        Threshold from calibration SSOT (default 0.50, v12 §4.2).
    conservative_route / conservative_tier:
        Injectable for tests; default to R3_GROUNDED / TIER_M per doctrine.

    Notes
    -----
    - Terminal routes (R1A, R1B, R5_FALLBACK) are NEVER overridden — if the
      classifier is low-confidence but the route is a cache hit or abstain,
      the decision stands on its own merits (the hit/abstain signal is
      stronger than classifier probability).
    - If the top-pick is already the conservative route, no override is
      applied (idempotent).
    """
    if not 0.0 <= classifier_confidence <= 1.0:
        raise ValueError(f"classifier_confidence out of range [0,1]: {classifier_confidence}")
    _terminal = {RouteId.R1A, RouteId.R1B, RouteId.R5_FALLBACK}
    if top_pick in _terminal:
        return ColdStartDecision(
            overridden=False,
            route_id=top_pick,
            cost_tier=top_pick_tier,
            fallback_chain_prefix=(),
            reason_codes=(),
        )
    if classifier_confidence >= cold_start_threshold:
        return ColdStartDecision(
            overridden=False,
            route_id=top_pick,
            cost_tier=top_pick_tier,
            fallback_chain_prefix=(),
            reason_codes=(),
        )
    if top_pick == conservative_route and top_pick_tier == conservative_tier:
        return ColdStartDecision(
            overridden=False,
            route_id=top_pick,
            cost_tier=top_pick_tier,
            fallback_chain_prefix=(),
            reason_codes=("cold_start_already_conservative",),
        )
    return ColdStartDecision(
        overridden=True,
        route_id=conservative_route,
        cost_tier=conservative_tier,
        fallback_chain_prefix=(FallbackEntry(route_id=top_pick, cost_tier=top_pick_tier),),
        reason_codes=("cold_start_override",),
    )
