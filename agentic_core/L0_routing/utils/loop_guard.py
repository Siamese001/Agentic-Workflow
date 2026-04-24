"""v12 §8 — Loop Guard.

Cross-route loop detection via agent efficiency score:

    agent_efficiency_score = unique_productive_spans / total_spans

A "productive" span is one that emitted a new artifact or mutated state
(tracked by the caller). If the score falls below
``loop_guard_efficiency_threshold`` across ``>= min_spans_for_loop_guard``
spans within a single trace, ``LoopSuspected`` fires.

Complements v11's "forward-only L3, no backward edges" — that invariant
prevents intra-run loops. This guard catches cross-request/cross-route
loops where the same user session keeps re-entering the dispatcher and
making no progress.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LoopGuardVerdict:
    """Output of ``evaluate_loop_guard``.

    Attributes
    ----------
    suspected:
        True iff the loop guard considers this trace to be looping.
    efficiency_score:
        The computed score, or ``-1.0`` if insufficient data.
    span_count:
        Total spans considered.
    productive_span_count:
        Unique productive spans considered.
    reason:
        Human-readable explanation, safe for telemetry.
    """

    suspected: bool
    efficiency_score: float
    span_count: int
    productive_span_count: int
    reason: str


def evaluate_loop_guard(
    span_ids: list[str],
    productive_span_ids: set[str],
    efficiency_threshold: float,
    min_spans: int,
) -> LoopGuardVerdict:
    """Compute the agent-efficiency verdict for one trace.

    Parameters
    ----------
    span_ids:
        All span ids in the trace (duplicates allowed — list, not set —
        because the same span can appear in the stream more than once
        without being productive each time).
    productive_span_ids:
        Set of span ids that emitted a new artifact or state mutation.
        MUST be a subset of ``set(span_ids)``; violations raise ValueError.
    efficiency_threshold:
        From calibration SSOT (default 0.40, v12 §4.2).
    min_spans:
        Minimum total spans before the guard can fire (default 5).
        Prevents false-positive firing on short traces.
    """
    total = len(span_ids)
    if total == 0:
        return LoopGuardVerdict(
            suspected=False,
            efficiency_score=-1.0,
            span_count=0,
            productive_span_count=0,
            reason="empty_trace",
        )
    unique_spans = set(span_ids)
    stray = productive_span_ids - unique_spans
    if stray:
        raise ValueError(f"productive_span_ids contains span ids not in span_ids: {sorted(stray)[:3]}")
    productive = len(productive_span_ids)
    if total < min_spans:
        return LoopGuardVerdict(
            suspected=False,
            efficiency_score=productive / total,
            span_count=total,
            productive_span_count=productive,
            reason=f"insufficient_spans({total}<{min_spans})",
        )
    score = productive / total
    if score < efficiency_threshold:
        return LoopGuardVerdict(
            suspected=True,
            efficiency_score=score,
            span_count=total,
            productive_span_count=productive,
            reason=(f"efficiency {score:.3f} < threshold {efficiency_threshold:.3f} across {total} spans"),
        )
    return LoopGuardVerdict(
        suspected=False,
        efficiency_score=score,
        span_count=total,
        productive_span_count=productive,
        reason=f"healthy efficiency {score:.3f}",
    )
