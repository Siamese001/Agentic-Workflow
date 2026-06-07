"""L2 Routing Gates — Gate 0-4 overrides applied on top of ConfidenceScorer tier.

Wave 2 P2.1 of `docs/archive/windsurf/legacy-tree/plans/routing-unification-qwen-abe735.md`.

Ports the Gate 0-4 override semantics from the legacy L_OPS
`_ssot_routing.compute_routing_decision` into L2 (where the rest of the
healing pipeline lives). The legacy computation of an integer score
S = 3C+4B+3A+2N+4F is NOT re-ported here; the `ConfidenceScorer` already
produces a `HealTier`. Gates only *override* that tier when structural /
replay / retry / hard-override conditions apply.

Gate precedence (matches _ssot_routing.py:175-237):

    Gate 0 — replay_mode                  → HIGH (deterministic)
    Gate 1 — retry_count >= 3             → LOW (escalate to Pro);
                                             HITL if provider prohibited
    Gate 2 — structural failure type      → LOW unless deterministic_coverage;
                                             HITL if provider prohibited
    Gate 4 — B3/F3 hard override          → LOW;
                                             HITL if both providers prohibited
    Qwen-disallowed post-filter           → if initial tier is MEDIUM and
                                             failure type is in
                                             QWEN_DISALLOWED_FAILURE_TYPES,
                                             escalate to LOW (or HITL if
                                             Gemini prohibited)

Gate 3 (critical-surface mechanical coverage, S1's B=3 A=0 playbook_match
path) is not ported; it encodes an integer-score heuristic that has no
direct counterpart in the tier-based model. Callers that need it should
pre-bias the ConfidenceScorer.

All gates are pure functions with no side effects.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from agentic_core.L0_routing.config.model_registry import (
    QWEN_DISALLOWED_FAILURE_TYPES,
)  # guardian: allow-layer-violation -- L2 healer reads failure-type constants from L0 SSOT

from .confidence_scorer import HealTier

if TYPE_CHECKING:
    from .failure_signal import FailureSignal


# ============================================================================
# Structural failure-type set (matches _ssot_types._STRUCTURAL_CLASS)
# ============================================================================

STRUCTURAL_FAILURE_TYPES: frozenset[str] = frozenset(
    {
        "LAYER_VIOLATION",
        "GATEWAY_BYPASS",
        "KILL_SWITCH_BYPASS",
        "SIGNATURE_VERIFY",
        "UNSIGNED_INGRESS",
    },
)
"""Subset of QWEN_DISALLOWED_FAILURE_TYPES that trigger Gate 2 structural routing."""


# ============================================================================
# RoutingContext — optional routing metadata accompanying a FailureSignal
# ============================================================================


@dataclass(frozen=True)
class RoutingContext:
    """Routing-layer metadata that is NOT intrinsic to FailureSignal.

    All fields default to False / empty-string so callers can construct a
    bare RoutingContext() for "no overrides, pure tier" routing.
    """

    replay_mode: bool = False
    """True when the current run is a deterministic replay (Gate 0)."""

    playbook_match: bool = False
    """True when a known playbook already covers this failure signature."""

    deterministic_coverage: bool = False
    """True when a deterministic rule-based agent can resolve this failure."""

    provider_prohibited_gemini: bool = False
    """True when Gemini provider is unavailable (API key missing, budget exhausted)."""

    provider_prohibited_qwen: bool = False
    """True when local Qwen vLLM is unavailable (server down, OOM)."""

    failure_type: str = ""
    """
    Structural failure-type string matching _ssot_types.FailureType values
    (e.g. "LAYER_VIOLATION", "IMPORT_BOUNDARY_VIOLATION"). Empty string
    means unknown / non-structural.
    """

    cost_budget_remaining_usd: float | None = None
    """
    Monthly cost budget remaining in USD. When None (default), cost-weighted
    demotion is disabled. When a number is provided, Wave 6 P6.2 demotion
    logic in `HealingRouter.route()` downgrades to cheaper tiers under
    budget pressure:

      - budget < COST_DEMOTE_PRO_THRESHOLD  → Pro demoted to Flash
      - budget < COST_DEMOTE_FLASH_THRESHOLD → Flash demoted to Qwen (free local)

    Defaults configurable via env vars ROUTING_COST_DEMOTE_PRO_USD and
    ROUTING_COST_DEMOTE_FLASH_USD (see `healing_router.py`).
    """


# ============================================================================
# Gate evaluation
# ============================================================================


def apply_routing_gates(
    initial_tier: HealTier,
    signal: FailureSignal,
    context: RoutingContext | None = None,
) -> tuple[HealTier, str]:
    """Apply Gate 0-4 overrides on top of a ConfidenceScorer-produced tier.

    Args:
        initial_tier: Tier returned by `ConfidenceScorer.score(signal).tier`.
        signal: The FailureSignal being routed.
        context: Optional routing metadata. If None, a default (all-False)
            RoutingContext is used — gates produce no overrides.

    Returns:
        (final_tier, gate_name) where gate_name is one of:
            "GATE_0_REPLAY"
            "GATE_1_RETRY_OVERRIDE"
            "GATE_1_RETRY_OVERRIDE_HITL"
            "GATE_2_STRUCTURAL_NO_DET_COV"
            "GATE_2_STRUCTURAL_DET_COV"
            "GATE_2_STRUCTURAL_HITL"
            "GATE_4_HARD_OVERRIDE"
            "GATE_4_HARD_OVERRIDE_HITL"
            "QWEN_DISALLOWED"
            "QWEN_DISALLOWED_HITL"
            "NO_OVERRIDE" — initial_tier used as-is
    """
    ctx = context or RoutingContext()

    # Gate 0: replay mode → always deterministic
    if ctx.replay_mode:
        return (HealTier.HIGH, "GATE_0_REPLAY")

    # Gate 1: retry exhaustion → escalate to high-reasoning (Pro)
    if signal.retry_count >= 3:
        if ctx.provider_prohibited_gemini:
            return (HealTier.HITL, "GATE_1_RETRY_OVERRIDE_HITL")
        return (HealTier.LOW, "GATE_1_RETRY_OVERRIDE")

    # Gate 2: structural failure → escalate (unless deterministic coverage)
    if ctx.failure_type in STRUCTURAL_FAILURE_TYPES:
        if ctx.deterministic_coverage:
            return (HealTier.HIGH, "GATE_2_STRUCTURAL_DET_COV")
        if ctx.provider_prohibited_gemini:
            return (HealTier.HITL, "GATE_2_STRUCTURAL_HITL")
        return (HealTier.LOW, "GATE_2_STRUCTURAL_NO_DET_COV")

    # Gate 4: hard-override — encoded via budget_remaining + retry_count
    # High budget pressure (< 0.10) AND non-zero retries AND no deterministic
    # coverage means "escalate regardless of tier".
    hard_override = (
        signal.budget_remaining < 0.10 and signal.retry_count >= 1 and not ctx.deterministic_coverage
    )
    if hard_override:
        if ctx.provider_prohibited_gemini and ctx.provider_prohibited_qwen:
            return (HealTier.HITL, "GATE_4_HARD_OVERRIDE_HITL")
        return (HealTier.LOW, "GATE_4_HARD_OVERRIDE")

    # Qwen-disallowed post-filter: if tier says MEDIUM but failure type
    # forbids Qwen, escalate to LOW (or HITL if Gemini unavailable).
    if initial_tier == HealTier.MEDIUM and ctx.failure_type in QWEN_DISALLOWED_FAILURE_TYPES:
        if ctx.provider_prohibited_gemini:
            return (HealTier.HITL, "QWEN_DISALLOWED_HITL")
        return (HealTier.LOW, "QWEN_DISALLOWED")

    # Provider-unavailable fallbacks for the initial tier:
    if initial_tier == HealTier.MEDIUM and ctx.provider_prohibited_qwen:
        if ctx.provider_prohibited_gemini:
            return (HealTier.HITL, "QWEN_UNAVAILABLE_HITL")
        return (HealTier.LOW, "QWEN_UNAVAILABLE_FALLBACK")
    if initial_tier == HealTier.LOW and ctx.provider_prohibited_gemini:
        return (HealTier.HITL, "GEMINI_UNAVAILABLE_HITL")

    return (initial_tier, "NO_OVERRIDE")


__all__ = [
    "STRUCTURAL_FAILURE_TYPES",
    "RoutingContext",
    "apply_routing_gates",
]
