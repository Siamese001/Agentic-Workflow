"""Healing outcome types for L2.3 → Meta-Learning feedback loop.

Immutable, frozen dataclasses for deterministic healing outcome tracking.

Invariants:
  - All types are frozen dataclasses with slots
  - No wall-clock reads; timestamp_utc provided by caller
  - Stable rounding: round-half-up to 4 decimal places via QUANTIZE
  - Proposal is container-only; no config/routing/L4 writes
"""

from __future__ import annotations

import decimal
from dataclasses import dataclass, field

# Stable rounding context: round-half-up to 4 decimal places.
_ROUND_CTX = decimal.Context(rounding=decimal.ROUND_HALF_UP)
_QUANT = decimal.Decimal("0.0001")


def _stable_rate(numerator: int, denominator: int) -> float:
    """Compute rate with stable round-half-up to 4 decimal places.

    Returns 0.0 when denominator is zero.
    """
    if denominator == 0:
        return 0.0
    raw = decimal.Decimal(numerator) / decimal.Decimal(denominator)
    rounded = raw.quantize(_QUANT, context=_ROUND_CTX)
    return float(rounded)


# =============================================================================
# HealingOutcomeEvent — single invocation outcome
# =============================================================================


@dataclass(frozen=True, slots=True)
class HealingOutcomeEvent:
    """Immutable record of a single L2.3 healing invocation outcome.

    Attributes
    ----------
    healer_id : str
        Canonical healer identity (e.g. check_id or healer function name).
    tier : str
        Healing tier used (e.g. 'LOCAL_AGENT', 'QWEN_VLLM', 'GEMINI_2_5_PRO').
    failure_type : str
        Stable failure category string.
    success : bool
        Whether the healing invocation succeeded.
    timestamp_utc : int
        Caller-provided Unix timestamp (aggregator never reads wall-clock).
    trace_id : str | None
        Optional correlation ID for tracing.
    error_signature : str | None
        Optional deterministic hash/signature of the error (if already available).
    """

    healer_id: str
    tier: str
    failure_type: str
    success: bool
    timestamp_utc: int
    trace_id: str | None = None
    error_signature: str | None = None
    failure_vector: tuple[float, ...] | None = None
    routing_digest: str | None = None
    confidence_score: float | None = None
    novelty_flag: bool = False
    files_touched: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.healer_id:
            raise ValueError("healer_id must not be empty")
        if not self.tier:
            raise ValueError("tier must not be empty")
        if not self.failure_type:
            raise ValueError("failure_type must not be empty")


# =============================================================================
# HealingOutcomeStats — aggregated counters per (healer_id, tier, failure_type)
# =============================================================================


@dataclass(frozen=True, slots=True)
class HealingOutcomeStats:
    """Deterministic aggregate counters for a single (healer_id, tier, failure_type) key.

    Rounding rule: round-half-up to 4 decimal places (via ``_stable_rate``).

    Attributes
    ----------
    healer_id : str
        Canonical healer identity.
    tier : str
        Healing tier.
    failure_type : str
        Stable failure category.
    total_count : int
        Total events ingested for this key.
    success_count : int
        Number of successful outcomes.
    failure_count : int
        Number of failed outcomes.
    success_rate : float
        success_count / total_count, rounded half-up to 4 decimals.
    """

    healer_id: str
    tier: str
    failure_type: str
    total_count: int
    success_count: int
    failure_count: int
    success_rate: float

    @staticmethod
    def from_counts(
        healer_id: str,
        tier: str,
        failure_type: str,
        success_count: int,
        failure_count: int,
    ) -> HealingOutcomeStats:
        """Build stats from raw counts with stable rounding."""
        total = success_count + failure_count
        return HealingOutcomeStats(
            healer_id=healer_id,
            tier=tier,
            failure_type=failure_type,
            total_count=total,
            success_count=success_count,
            failure_count=failure_count,
            success_rate=_stable_rate(success_count, total),
        )


# =============================================================================
# HealingOutcomeProposal — proposal-only container (Phase 1: no-op)
# =============================================================================


@dataclass(frozen=True, slots=True)
class HealingOutcomeProposal:
    """Proposal-only container for healing outcome-based optimizations.

    Phase 1: this is intentionally a no-op container.  It carries the
    snapshot from which a future phase may derive threshold adjustments.
    It MUST NOT write files, mutate configs, or call external services.

    Attributes
    ----------
    stats : tuple[HealingOutcomeStats, ...]
        Deterministically ordered stats snapshot driving this proposal.
    recommended_actions : tuple[str, ...]
        Human-readable action descriptions (empty in Phase 1).
    """

    stats: tuple[HealingOutcomeStats, ...] = field(default_factory=tuple)
    recommended_actions: tuple[str, ...] = field(default_factory=tuple)


__all__ = [
    "HealingOutcomeEvent",
    "HealingOutcomeProposal",
    "HealingOutcomeStats",
]
