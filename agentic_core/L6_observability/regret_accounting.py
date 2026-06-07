"""Cross-layer regret accounting — end-to-end counterfactual replay.

Plan: ``docs/archive/windsurf/legacy-tree/plans/routing-decision-process-enhancement-9c7e4d.md`` Wave W13.

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

import logging
import threading
from collections import defaultdict
from dataclasses import dataclass, field

_LOGGER = logging.getLogger(__name__)

# Constitutional §29 closed-loop wiring (W5.3). Lazy singleton so this module
# stays importable when `tools.ledgers` is absent.
_REGRET_HELPER = None  # type: ignore[var-annotated]


def _get_regret_helper():
    global _REGRET_HELPER  # noqa: PLW0603
    if _REGRET_HELPER is not None:
        return _REGRET_HELPER
    try:
        from tools.ledgers.router_helper import RouterClosedLoopHelper  # noqa: PLC0415

        _REGRET_HELPER = RouterClosedLoopHelper(
            layer="L6",
            router="regret",
            ledger_name="router_l6_regret",
            repo_area="agentic_core/L6_observability/regret_accounting.py",
        )
        return _REGRET_HELPER
    except ImportError:  # guardian: allow-log-and-swallow -- helper unavailable must not break regret accounting
        _LOGGER.debug("RouterClosedLoopHelper unavailable for L6/regret", exc_info=True)
        return None


def _record_regret_sample(sample: "DecisionRegretSample") -> None:
    """Constitutional §29 — durable write of one regret sample.

    Records the sample with its decision_layer as the ``selected`` field so
    posterior aggregation by layer comes for free. ``predicted_p_success``
    uses the chosen reward clamped to [0, 1]; ``eu_score`` carries -regret
    (more negative = worse decision in expectation).

    Fail-soft: any helper failure is swallowed.
    """
    helper = _get_regret_helper()
    if helper is None:
        return
    try:
        chosen = float(sample.chosen_reward)
        regret = float(sample.regret)
        helper.record_decision(
            selected=str(sample.decision_layer),
            cell={"decision_layer": str(sample.decision_layer)},
            predicted_p_success=max(0.0, min(1.0, chosen)),
            eu_score=-regret,
            decision_id=str(sample.decision_id),
            prediction_extras={
                "chosen_reward": chosen,
                "best_alternative_reward": float(sample.best_alternative_reward),
                "regret": regret,
            },
        )
    except (AttributeError, TypeError, ValueError, RuntimeError):  # guardian: allow-log-and-swallow -- ledger emission is best-effort; regret accounting must never break
        _LOGGER.debug("regret_accounting ledger emit failed", exc_info=True)

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
    """Thread-safe accumulator over a session / window.

    W5.3 (closed-loop-l6-promo-regret-wiring-e3c5b9): every ``record`` call
    now ALSO writes a durable row to ``router_l6_regret`` ledger via the
    `RouterClosedLoopHelper` so meta-learning can attribute regret across
    process restarts. The in-memory list is preserved for fast aggregation.
    """

    _samples: list[DecisionRegretSample] = field(default_factory=list)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def record(self, sample: DecisionRegretSample) -> None:
        with self._lock:
            self._samples.append(sample)
        # Constitutional §29 — fail-soft durable write
        _record_regret_sample(sample)

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
