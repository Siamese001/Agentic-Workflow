"""Trajectory divergence scorer — G4 (plan ``system-learning-waves-7b3c91`` B1).

Localizes **where** two agent trajectories diverge. The existing replay
validators (:mod:`system_learning.engines.replay_validator`,
:mod:`system_learning.engines.deterministic_replay_engine`) emit exact-match
signals; this module adds the missing *localized* signal: given a baseline
trajectory and a replay trajectory, it returns the first divergent span, the
category of divergence, and a normalized distance in ``[0.0, 1.0]``.

Design (Sakura primitive 7 + arXiv 2505.17716):

- Inputs are normalized sequences of :class:`TrajectorySpan` records — each
  span is (``step_index``, ``tool_name``, ``tool_args``, ``tool_result_hash``,
  ``model_name``, ``stub_id``). Callers project OTel / replay traces into
  this shape; keeping the scorer format-agnostic avoids coupling to the
  heavy ``lifecycle_trace_contract`` emitter machinery used elsewhere.
- Divergence categories, checked in order:
    1. ``missing_span`` — one trajectory is shorter at the mismatch index.
    2. ``tool_changed`` — different tool invoked at the same step.
    3. ``arg_changed`` — same tool, different args (argument-diff map provided).
    4. ``model_changed`` — same tool+args, different model metadata.
    5. ``stub_miss`` — baseline used a real model, replay used a stub (or vv).
    6. ``result_changed`` — same inputs, different deterministic result hash.
- Distance = (# divergent spans) / max(len(baseline), len(replay)).
- No I/O, no global state — pure function library so consumers
  (``replay_validator``, ``approval_gauntlet_engine``) can opt-in without
  taking a hard dependency.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Sequence

# Divergence categories in priority order (first match wins per span).
DIVERGENCE_CATEGORIES = (
    "missing_span",
    "tool_changed",
    "arg_changed",
    "model_changed",
    "stub_miss",
    "result_changed",
)


@dataclass(frozen=True)
class TrajectorySpan:
    """Normalized span for divergence scoring.

    Consumers project OTel spans / replay events into this shape. ``tool_args``
    is a mapping of JSON-serializable values; use a stable canonicalization on
    the producer side if floating-point tolerance is needed.
    """

    step_index: int
    tool_name: str
    tool_args: Mapping[str, Any] = field(default_factory=dict)
    tool_result_hash: str = ""
    model_name: str = ""
    stub_id: str = ""


@dataclass(frozen=True)
class DivergencePoint:
    """First divergent span located by the scorer."""

    step_index: int
    category: str
    baseline_span: TrajectorySpan | None
    replay_span: TrajectorySpan | None
    # Argument-level diff when category == "arg_changed": {arg_name: (base_value, replay_value)}.
    arg_diff: Mapping[str, tuple[Any, Any]] = field(default_factory=dict)
    note: str = ""


@dataclass(frozen=True)
class DivergenceReport:
    """Result of :func:`score_divergence`.

    ``distance`` is in ``[0.0, 1.0]``: 0.0 means the trajectories are
    identical; 1.0 means no span matched at any index (total divergence).
    ``first_divergence`` is ``None`` iff ``distance == 0.0``.
    """

    distance: float
    divergent_span_count: int
    total_spans: int
    first_divergence: DivergencePoint | None
    all_divergences: Sequence[DivergencePoint] = field(default_factory=tuple)


def _diff_args(baseline: Mapping[str, Any], replay: Mapping[str, Any]) -> dict[str, tuple[Any, Any]]:
    """Return a map of arg_name -> (baseline_value, replay_value) for changed args."""

    diff: dict[str, tuple[Any, Any]] = {}
    keys = set(baseline) | set(replay)
    _MISSING = object()
    for key in keys:
        base_val = baseline.get(key, _MISSING)
        replay_val = replay.get(key, _MISSING)
        if base_val != replay_val:
            diff[key] = (
                None if base_val is _MISSING else base_val,
                None if replay_val is _MISSING else replay_val,
            )
    return diff


def _classify_span_pair(
    baseline: TrajectorySpan | None, replay: TrajectorySpan | None
) -> DivergencePoint | None:
    """Classify a single span-pair. Returns ``None`` if the spans agree."""

    if baseline is None or replay is None:
        present = replay if baseline is None else baseline
        index = present.step_index if present is not None else -1
        return DivergencePoint(
            step_index=index,
            category="missing_span",
            baseline_span=baseline,
            replay_span=replay,
            note="one trajectory ended before the other",
        )

    if baseline.tool_name != replay.tool_name:
        return DivergencePoint(
            step_index=baseline.step_index,
            category="tool_changed",
            baseline_span=baseline,
            replay_span=replay,
            note=f"baseline={baseline.tool_name!r} replay={replay.tool_name!r}",
        )

    arg_diff = _diff_args(baseline.tool_args, replay.tool_args)
    if arg_diff:
        return DivergencePoint(
            step_index=baseline.step_index,
            category="arg_changed",
            baseline_span=baseline,
            replay_span=replay,
            arg_diff=arg_diff,
        )

    if baseline.model_name != replay.model_name:
        return DivergencePoint(
            step_index=baseline.step_index,
            category="model_changed",
            baseline_span=baseline,
            replay_span=replay,
            note=f"baseline_model={baseline.model_name!r} replay_model={replay.model_name!r}",
        )

    # stub_miss: exactly one side is using a stub.
    baseline_stubbed = bool(baseline.stub_id)
    replay_stubbed = bool(replay.stub_id)
    if baseline_stubbed != replay_stubbed:
        return DivergencePoint(
            step_index=baseline.step_index,
            category="stub_miss",
            baseline_span=baseline,
            replay_span=replay,
            note=f"baseline_stub={baseline.stub_id!r} replay_stub={replay.stub_id!r}",
        )

    if baseline.tool_result_hash != replay.tool_result_hash:
        return DivergencePoint(
            step_index=baseline.step_index,
            category="result_changed",
            baseline_span=baseline,
            replay_span=replay,
            note=(
                f"baseline_hash={baseline.tool_result_hash[:16]!r} "
                f"replay_hash={replay.tool_result_hash[:16]!r}"
            ),
        )

    return None


def score_divergence(
    baseline: Iterable[TrajectorySpan],
    replay: Iterable[TrajectorySpan],
) -> DivergenceReport:
    """Score divergence between ``baseline`` and ``replay`` span streams.

    Both inputs are consumed in order; callers are responsible for sorting
    by ``step_index`` if their producers emit out-of-order.
    """

    baseline_list = list(baseline)
    replay_list = list(replay)
    total = max(len(baseline_list), len(replay_list))
    if total == 0:
        return DivergenceReport(
            distance=0.0,
            divergent_span_count=0,
            total_spans=0,
            first_divergence=None,
            all_divergences=(),
        )

    divergences: list[DivergencePoint] = []
    for idx in range(total):
        base_span = baseline_list[idx] if idx < len(baseline_list) else None
        replay_span = replay_list[idx] if idx < len(replay_list) else None
        point = _classify_span_pair(base_span, replay_span)
        if point is not None:
            divergences.append(point)

    first = divergences[0] if divergences else None
    return DivergenceReport(
        distance=len(divergences) / total,
        divergent_span_count=len(divergences),
        total_spans=total,
        first_divergence=first,
        all_divergences=tuple(divergences),
    )


def localize_first_divergence(
    baseline: Iterable[TrajectorySpan],
    replay: Iterable[TrajectorySpan],
) -> DivergencePoint | None:
    """Convenience wrapper returning only the first divergent span.

    Equivalent to ``score_divergence(...).first_divergence``.
    """

    return score_divergence(baseline, replay).first_divergence
