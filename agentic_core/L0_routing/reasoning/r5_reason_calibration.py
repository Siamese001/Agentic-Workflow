"""R5 reason-code calibration — per-trigger Brier + auto-demote.

Plan: ``docs/archive/windsurf/legacy-tree/plans/routing-decision-process-enhancement-9c7e4d.md`` Wave W5.

Closes opportunity 1.4: today the multi-signal R5 path treats all 6 triggers
(``low_confidence``, ``ood_score``, ``circuit_breaker_open``, ``budget_exceeded``,
``clarification_needed``, ``toxicity_flagged``) as equal authority. One bad
trigger silently dominates and starves real signal.

This module:

1. Computes per-reason Brier score from ``decision_events`` rows whose
   ``reason_codes_json`` includes the reason and ``outcome_success`` is set.
2. Auto-demotes a reason when its Brier exceeds a threshold for at least
   ``min_observations`` samples — demoted reasons are returned in the
   ``demoted`` set so the routing layer can deprioritize or require a
   second signal before acting on them.

Design:

* Pure function over a connection — no global state.
* Brier convention: a reason is "right" when triggering it preceded a
  failed outcome (``outcome_success=False``). Higher Brier = noisier reason.
* ``analyze_r5_reasons`` returns a typed report; callers persist it via
  whatever channel they prefer (today: JSON dump; future: dedicated
  ``r5_reason_calibration`` table).
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field

# Closed vocabulary mirrors ``R5Signals`` keys in
# ``agentic_core/runtime/contracts/abstain_contract.py`` plus the
# scalar ``low_confidence`` baseline trigger.
KNOWN_R5_REASONS: frozenset[str] = frozenset(
    {
        "low_confidence",
        "ood_score",
        "circuit_breaker_open",
        "budget_exceeded",
        "clarification_needed",
        "toxicity_flagged",
    },
)


@dataclass(frozen=True)
class ReasonCalibration:
    """Per-reason summary statistics."""

    reason: str
    n_observations: int
    brier_score: float
    success_rate_when_triggered: float
    demoted: bool


@dataclass
class R5CalibrationReport:
    """Aggregate report over all observed R5 reasons."""

    per_reason: dict[str, ReasonCalibration] = field(default_factory=dict)
    demoted: set[str] = field(default_factory=set)
    insufficient_data: set[str] = field(default_factory=set)

    def to_dict(self) -> dict[str, object]:
        return {
            "per_reason": {
                k: {
                    "reason": v.reason,
                    "n_observations": v.n_observations,
                    "brier_score": v.brier_score,
                    "success_rate_when_triggered": v.success_rate_when_triggered,
                    "demoted": v.demoted,
                }
                for k, v in self.per_reason.items()
            },
            "demoted": sorted(self.demoted),
            "insufficient_data": sorted(self.insufficient_data),
        }


def _brier_score(predictions: list[tuple[float, bool]]) -> float:
    """Mean (predicted - actual)^2. Empty list → 0.0."""
    if not predictions:
        return 0.0
    total = 0.0
    for pred, actual in predictions:
        target = 1.0 if actual else 0.0
        total += (pred - target) ** 2
    return total / len(predictions)


def analyze_r5_reasons(
    conn: sqlite3.Connection,
    *,
    brier_demote_threshold: float = 0.30,
    min_observations: int = 20,
    since_timestamp: float | None = None,
) -> R5CalibrationReport:
    """Compute per-reason calibration over recent R5 dispatches.

    Args:
        conn: SQLite connection with the ``decision_events`` table.
        brier_demote_threshold: A reason whose Brier exceeds this AND has at
            least ``min_observations`` samples is auto-demoted.
        min_observations: Minimum row count before demotion can fire.
        since_timestamp: Optional epoch lower-bound for the window.

    Returns:
        :class:`R5CalibrationReport` with per-reason stats and a ``demoted``
        set of reason codes the router should deprioritize.

    Notes:
        Brier convention here: when a reason fires, the *predicted* failure
        probability is 1.0 (R5 is the abstain path — triggering it claims
        "we expect this to fail"). The *actual* outcome is ``not outcome_success``.
        So a reason is well-calibrated iff its triggered dispatches were
        followed by failures.
    """
    sql = (
        "SELECT reason_codes_json, outcome_success "
        "FROM decision_events "
        "WHERE chosen_route = 'R5' AND outcome_success IS NOT NULL"
    )
    params: tuple = ()
    if since_timestamp is not None:
        sql += " AND timestamp >= ?"
        params = (since_timestamp,)

    # Bucket Bernoulli draws per reason
    per_reason_buckets: dict[str, list[tuple[float, bool]]] = {}
    for raw_reasons, outcome in conn.execute(sql, params):
        try:
            reasons = json.loads(raw_reasons or "[]")
        except json.JSONDecodeError:
            continue
        if not isinstance(reasons, list):
            continue
        # R5 prediction: we expected failure, so predicted_failure = 1.0
        actual_failure = not bool(outcome)
        for reason in reasons:
            if reason not in KNOWN_R5_REASONS:
                continue
            per_reason_buckets.setdefault(reason, []).append((1.0, actual_failure))

    report = R5CalibrationReport()
    for reason, bucket in per_reason_buckets.items():
        n = len(bucket)
        brier = _brier_score(bucket)
        # Success-when-triggered = fraction of dispatches that DID succeed
        # despite the abstain trigger (i.e. the reason was a false alarm).
        false_alarms = sum(1 for _, actual_failure in bucket if not actual_failure)
        sr_when_triggered = false_alarms / n if n else 0.0
        if n < min_observations:
            report.insufficient_data.add(reason)
            demoted = False
        else:
            demoted = brier > brier_demote_threshold
            if demoted:
                report.demoted.add(reason)
        report.per_reason[reason] = ReasonCalibration(
            reason=reason,
            n_observations=n,
            brier_score=brier,
            success_rate_when_triggered=sr_when_triggered,
            demoted=demoted,
        )
    return report


__all__ = [
    "KNOWN_R5_REASONS",
    "R5CalibrationReport",
    "ReasonCalibration",
    "analyze_r5_reasons",
]
