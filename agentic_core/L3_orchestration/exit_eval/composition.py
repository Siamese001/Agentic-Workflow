"""Composition modes — binary / weighted / hybrid.

See ``grader_composition_spec.md`` §3.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from agentic_core.L3_orchestration.exit_eval.dimension import DimensionResult


class CompositionMode(str, Enum):
    """How dimension scores combine into a gate disposition."""

    BINARY = "binary"
    WEIGHTED = "weighted"
    HYBRID = "hybrid"


@dataclass(frozen=True)
class AggregateResult:
    """Outcome of applying a composition mode to a set of dimension results.

    ``passed`` is authoritative. ``aggregate_score`` and
    ``aggregate_threshold`` are populated for weighted / hybrid and reported
    to BUS P and OTel spans; ``None`` in binary mode.
    """

    passed: bool
    mode: CompositionMode
    aggregate_score: float | None
    aggregate_threshold: float | None
    hard_gate_failures: tuple[str, ...] = field(default_factory=tuple)
    weighted_pass: bool | None = None


def compose(
    results: list[DimensionResult],
    *,
    mode: CompositionMode,
    aggregate_threshold: float | None = None,
) -> AggregateResult:
    """Combine dimension results under a composition mode.

    Rules (grader_composition_spec §3):

    - **Binary**: every dimension must meet its per-dimension threshold.
      ``aggregate_threshold`` is ignored.
    - **Weighted**: weighted average of scores must be >=
      ``aggregate_threshold``. Hard-gate flags are ignored in pure weighted
      mode; use ``HYBRID`` if both hard and soft sub-gates are needed.
    - **Hybrid**: all ``is_hard_gate`` dimensions must meet their thresholds
      (AND), AND the weighted average of the non-hard dimensions must meet
      ``aggregate_threshold``.

    Abstain propagation: any dimension with ``abstain=True`` forces
    ``passed=False`` regardless of mode. Callers are responsible for routing
    the abstain case to HITL rather than to deny.
    """
    if not results:
        raise ValueError("compose requires at least one DimensionResult")

    abstained = any(r.abstain for r in results)

    if mode is CompositionMode.BINARY:
        passed = all(r.passed for r in results) and not abstained
        return AggregateResult(
            passed=passed,
            mode=mode,
            aggregate_score=None,
            aggregate_threshold=None,
            hard_gate_failures=tuple(r.name for r in results if not r.passed),
        )

    if aggregate_threshold is None:
        raise ValueError(f"{mode.value} composition requires aggregate_threshold")

    if mode is CompositionMode.WEIGHTED:
        agg = _weighted_average(results)
        weighted_pass = agg >= aggregate_threshold
        return AggregateResult(
            passed=weighted_pass and not abstained,
            mode=mode,
            aggregate_score=agg,
            aggregate_threshold=aggregate_threshold,
            weighted_pass=weighted_pass,
        )

    # HYBRID
    hard = [r for r in results if r.is_hard_gate]
    soft = [r for r in results if not r.is_hard_gate]

    hard_failures = tuple(r.name for r in hard if not r.passed)
    hard_pass = not hard_failures

    if soft:
        agg = _weighted_average(soft)
        weighted_pass = agg >= aggregate_threshold
    else:
        agg = 1.0
        weighted_pass = True

    return AggregateResult(
        passed=hard_pass and weighted_pass and not abstained,
        mode=mode,
        aggregate_score=agg,
        aggregate_threshold=aggregate_threshold,
        hard_gate_failures=hard_failures,
        weighted_pass=weighted_pass,
    )


def _weighted_average(results: list[DimensionResult]) -> float:
    total_weight = sum(r.weight for r in results)
    if total_weight <= 0:
        raise ValueError("weighted composition requires at least one dimension with weight > 0")
    return sum(r.score * r.weight for r in results) / total_weight


__all__ = ["AggregateResult", "CompositionMode", "compose"]
