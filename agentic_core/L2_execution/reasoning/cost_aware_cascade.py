"""L2 R-CASC cost-aware escalation + provider fingerprint gate + Brier-by-provider.

Plan: ``docs/archive/windsurf/legacy-tree/plans/routing-decision-process-enhancement-9c7e4d.md`` Wave W8.

Closes opportunities 6.1 (cost-aware escalation replaces scalar 0.55), 6.2
(provider fingerprint drift gate), 6.3 (Brier-by-provider for chronic
over-confidence demotion).

Three independent surfaces:

1. :func:`should_escalate` — replaces scalar threshold with expected-utility
   comparator: escalate iff ``E[gain_at_higher_tier] > tier_cost_delta``.
2. :class:`ProviderFingerprintGate` — hard pre-call gate that rejects
   dispatch when the bound provider's fingerprint mismatches the snapshot.
3. :class:`ProviderConfidenceCalibrator` — per-provider Brier tracker;
   demotes providers whose Brier exceeds a threshold over enough samples.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field

ALLOWED_TIERS: tuple[str, ...] = ("TIER_S", "TIER_M", "TIER_L", "TIER_HITL")


def should_escalate(
    *,
    current_confidence: float,
    expected_gain_at_higher_tier: float,
    tier_cost_delta: float,
    safety_floor: float = 0.40,
) -> bool:
    """Return True iff expected utility of escalation outweighs cost.

    Args:
        current_confidence: Executor self-report at current tier, in [0, 1].
        expected_gain_at_higher_tier: Expected confidence delta from
            escalating, in [-1, 1] (negative means we expect regression).
        tier_cost_delta: Normalized cost of escalating, in [0, 1].
        safety_floor: Always escalate when current confidence is below this
            floor regardless of utility math (catastrophe avoidance).

    Returns:
        True to escalate, False to stay at the current tier.

    Raises:
        ValueError: When any input is outside its documented range.
    """
    if not 0.0 <= current_confidence <= 1.0:
        raise ValueError(f"current_confidence={current_confidence} out of [0,1]")
    if not -1.0 <= expected_gain_at_higher_tier <= 1.0:
        raise ValueError("expected_gain out of [-1,1]")
    if not 0.0 <= tier_cost_delta <= 1.0:
        raise ValueError(f"tier_cost_delta={tier_cost_delta} out of [0,1]")
    if not 0.0 <= safety_floor <= 1.0:
        raise ValueError(f"safety_floor={safety_floor} out of [0,1]")
    if current_confidence < safety_floor:
        return True
    return expected_gain_at_higher_tier > tier_cost_delta


class ProviderFingerprintMismatchError(RuntimeError):
    """Raised when the bound fingerprint contradicts the snapshot fingerprint."""


@dataclass
class ProviderFingerprintGate:
    """Hard pre-call gate: rejects dispatch on fingerprint drift.

    The orchestrator binds the snapshot fingerprint at L0 routing time;
    L2 verifies against the live provider fingerprint before any tool
    call. Mismatch raises and forces R5.
    """

    snapshot_fingerprints: dict[str, str] = field(default_factory=dict)

    def bind_snapshot(self, provider_id: str, fingerprint: str) -> None:
        self.snapshot_fingerprints[provider_id] = fingerprint

    def verify(self, provider_id: str, live_fingerprint: str) -> None:
        bound = self.snapshot_fingerprints.get(provider_id)
        if bound is None:
            # No bound fingerprint — first-time provider, accept and bind.
            self.snapshot_fingerprints[provider_id] = live_fingerprint
            return
        if bound != live_fingerprint:
            raise ProviderFingerprintMismatchError(
                f"provider={provider_id!r} fingerprint drift: "
                f"bound={bound!r} live={live_fingerprint!r}",
            )


@dataclass
class ProviderBrierStats:
    """Per-provider Brier accumulator."""

    provider_id: str
    n_observations: int = 0
    sum_squared_error: float = 0.0
    demoted: bool = False

    @property
    def brier_score(self) -> float:
        if self.n_observations == 0:
            return 0.0
        return self.sum_squared_error / self.n_observations


class ProviderConfidenceCalibrator:
    """Track Brier per provider; auto-demote chronic over-confident ones."""

    def __init__(
        self,
        *,
        brier_demote_threshold: float = 0.30,
        min_observations: int = 20,
    ) -> None:
        if not 0.0 <= brier_demote_threshold <= 1.0:
            raise ValueError("brier_demote_threshold out of [0,1]")
        if min_observations < 1:
            raise ValueError("min_observations must be >= 1")
        self._stats: dict[str, ProviderBrierStats] = {}
        self._lock = threading.Lock()
        self._brier_demote_threshold = brier_demote_threshold
        self._min_observations = min_observations

    def observe(self, provider_id: str, *, predicted_success: float, actual_success: bool) -> None:
        if not 0.0 <= predicted_success <= 1.0:
            raise ValueError("predicted_success out of [0,1]")
        target = 1.0 if actual_success else 0.0
        sq_err = (predicted_success - target) ** 2
        with self._lock:
            stats = self._stats.setdefault(
                provider_id,
                ProviderBrierStats(provider_id=provider_id),
            )
            stats.n_observations += 1
            stats.sum_squared_error += sq_err
            if (
                stats.n_observations >= self._min_observations
                and stats.brier_score > self._brier_demote_threshold
            ):
                stats.demoted = True

    def stats(self, provider_id: str) -> ProviderBrierStats:
        with self._lock:
            s = self._stats.get(provider_id)
            if s is None:
                return ProviderBrierStats(provider_id=provider_id)
            return ProviderBrierStats(
                provider_id=s.provider_id,
                n_observations=s.n_observations,
                sum_squared_error=s.sum_squared_error,
                demoted=s.demoted,
            )

    def demoted_providers(self) -> set[str]:
        with self._lock:
            return {p for p, s in self._stats.items() if s.demoted}


__all__ = [
    "ALLOWED_TIERS",
    "ProviderBrierStats",
    "ProviderConfidenceCalibrator",
    "ProviderFingerprintGate",
    "ProviderFingerprintMismatchError",
    "should_escalate",
]
