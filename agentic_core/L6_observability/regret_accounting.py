"""Cross-layer regret accounting — end-to-end counterfactual replay.

Plan: ``.windsurf/plans/routing-decision-process-enhancement-9c7e4d.md`` Wave W13.

Closes opportunity X.7 (cross-layer regret accounting). Per-layer learners
optimize their own arm; without an end-to-end accounting they can locally
improve while globally degrading. This module computes per-decision regret
defined as ``best_alternative_outcome - chosen_outcome`` across paired
counterfactual samples.

Surfaces:

1. :func:`per_decision_regret` — compute regret for one decision row given
   its chosen reward and the best alternative reward.
2. :func:`aggregate_regret_by_layer` — group decision-level regret by
   ``decision_layer`` to see which layer contributes the most regret.
3. :class:`RegretLedger` — accumulator usable from per-decision hooks;
   produces the per-layer aggregate at the end of a window.

Pure functions / data structures; persistence is the caller's choice
(typically: write a row into a ``decision_regret`` view over the
``decision_events`` table).
"""

from __future__ import annotations

import threading
from collections import defaultdict
from dataclasses import dataclass, field

from agentic_core.L6_observability.decision_events_schema import DECISION_LAYERS


@dataclass(frozen=True)
class DecisionRegretSample:
    """One decision's chosen vs best-alternative reward."""

    decision_id: str
    decision_layer: str
    chosen_reward: float
    best_alternative_reward: float

    @property
    def regret(self) -> float:
        """Non-negative regret in [0, max(reward) - min(reward)]."""
        delta = self.best_alternative_reward - self.chosen_reward
        return max(0.0, delta)


def per_decision_regret(
    *,
    decision_id: str,
    decision_layer: str,
    chosen_reward: float,
    best_alternative_reward: float,
) -> DecisionRegretSample:
    """Compute regret for one decision.

    Raises:
        ValueError: When ``decision_layer`` is unknown.
    """
    if decision_layer not in DECISION_LAYERS:
        raise ValueError(
            f"unknown decision_layer={decision_layer!r}; "
            f"allowed={sorted(DECISION_LAYERS)}",
        )
    return DecisionRegretSample(
        decision_id=decision_id,
        decision_layer=decision_layer,
        chosen_reward=chosen_reward,
        best_alternative_reward=best_alternative_reward,
    )


@dataclass(frozen=True)
class LayerRegretSummary:
    decision_layer: str
    n_samples: int
    sum_regret: float

    @property
    def mean_regret(self) -> float:
        if self.n_samples == 0:
            return 0.0
        return self.sum_regret / self.n_samples


def aggregate_regret_by_layer(
    samples: list[DecisionRegretSample],
) -> dict[str, LayerRegretSummary]:
    """Group regret by ``decision_layer``."""
    accum: dict[str, list[float]] = defaultdict(list)
    for s in samples:
        accum[s.decision_layer].append(s.regret)
    out: dict[str, LayerRegretSummary] = {}
    for layer, regrets in accum.items():
        out[layer] = LayerRegretSummary(
            decision_layer=layer,
            n_samples=len(regrets),
            sum_regret=sum(regrets),
        )
    return out


@dataclass
class RegretLedger:
    """Thread-safe accumulator over a session / window."""

    _samples: list[DecisionRegretSample] = field(default_factory=list)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def record(self, sample: DecisionRegretSample) -> None:
        with self._lock:
            self._samples.append(sample)

    def total_regret(self) -> float:
        with self._lock:
            return sum(s.regret for s in self._samples)

    def by_layer(self) -> dict[str, LayerRegretSummary]:
        with self._lock:
            return aggregate_regret_by_layer(list(self._samples))

    def top_offenders(self, k: int = 3) -> list[LayerRegretSummary]:
        """Return the top-k layers by total regret (descending)."""
        if k < 1:
            raise ValueError("k must be >= 1")
        summaries = list(self.by_layer().values())
        summaries.sort(key=lambda s: s.sum_regret, reverse=True)
        return summaries[:k]

    def reset(self) -> None:
        with self._lock:
            self._samples.clear()


__all__ = [
    "DecisionRegretSample",
    "LayerRegretSummary",
    "RegretLedger",
    "aggregate_regret_by_layer",
    "per_decision_regret",
]
