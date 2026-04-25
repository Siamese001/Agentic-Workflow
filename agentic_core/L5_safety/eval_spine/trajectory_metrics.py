"""Vertex-style trajectory metric suite (ADR-037 §2).

All metrics operate on lists of *canonical tool-call records* produced by
``tool_call_canonicalizer.canonicalize_tool_call``. A record is an object
with string fields ``tool`` and ``args_hash``. Two records are equivalent
iff both fields match.

Functions are pure — no I/O, no mutation.
"""

from __future__ import annotations

from collections import Counter
from typing import Final, Mapping, Sequence

_REQUIRED_FIELDS: Final[tuple[str, ...]] = ("tool", "args_hash")

ToolCallRecord = Mapping[str, str]


class TrajectoryRecordError(ValueError):
    """Raised when an input record does not have the canonical shape."""


def _validate(record: ToolCallRecord, index: int, source: str) -> tuple[str, str]:
    missing = [field for field in _REQUIRED_FIELDS if not record.get(field)]
    if missing:
        raise TrajectoryRecordError(f"{source}[{index}] missing required field(s): {missing}")
    tool = record["tool"]
    args = record["args_hash"]
    if not isinstance(tool, str) or not isinstance(args, str):
        raise TrajectoryRecordError(
            f"{source}[{index}] fields must be strings; got tool={tool!r} args_hash={args!r}"
        )
    return tool, args


def _as_tuples(records: Sequence[ToolCallRecord], source: str) -> list[tuple[str, str]]:
    return [_validate(record, index, source) for index, record in enumerate(records)]


def trajectory_exact_match(predicted: Sequence[ToolCallRecord], reference: Sequence[ToolCallRecord]) -> int:
    """Return 1 iff predicted is identical to reference (order + content)."""
    return 1 if _as_tuples(predicted, "predicted") == _as_tuples(reference, "reference") else 0


def trajectory_in_order_match(
    predicted: Sequence[ToolCallRecord], reference: Sequence[ToolCallRecord]
) -> int:
    """Return 1 iff reference appears as an ordered subsequence of predicted."""
    pred = _as_tuples(predicted, "predicted")
    ref = _as_tuples(reference, "reference")
    if not ref:
        return 1
    iterator = iter(pred)
    for item in ref:
        if not any(candidate == item for candidate in iterator):
            return 0
    return 1


def trajectory_any_order_match(
    predicted: Sequence[ToolCallRecord], reference: Sequence[ToolCallRecord]
) -> int:
    """Return 1 iff every reference record occurs in predicted (multiset)."""
    pred = Counter(_as_tuples(predicted, "predicted"))
    ref = Counter(_as_tuples(reference, "reference"))
    for key, count in ref.items():
        if pred[key] < count:
            return 0
    return 1


def trajectory_precision(predicted: Sequence[ToolCallRecord], reference: Sequence[ToolCallRecord]) -> float:
    """|predicted ∩ reference| / |predicted|; 0.0 if predicted is empty."""
    pred = _as_tuples(predicted, "predicted")
    if not pred:
        return 0.0
    ref = Counter(_as_tuples(reference, "reference"))
    remaining = Counter(ref)
    hits = 0
    for item in pred:
        if remaining.get(item, 0) > 0:
            hits += 1
            remaining[item] -= 1
    return hits / len(pred)


def trajectory_recall(predicted: Sequence[ToolCallRecord], reference: Sequence[ToolCallRecord]) -> float:
    """|predicted ∩ reference| / |reference|; 1.0 if reference is empty."""
    ref = _as_tuples(reference, "reference")
    if not ref:
        return 1.0
    pred = Counter(_as_tuples(predicted, "predicted"))
    hits = 0
    for item in ref:
        if pred.get(item, 0) > 0:
            hits += 1
            pred[item] -= 1
    return hits / len(ref)


def single_tool_use(predicted: Sequence[ToolCallRecord], tool_name: str) -> dict[str, object]:
    """Return ``{tool_name, present}`` — presence of ``tool_name`` in predicted."""
    if not isinstance(tool_name, str) or not tool_name:
        raise TrajectoryRecordError(f"tool_name must be non-empty string, got {tool_name!r}")
    pred = _as_tuples(predicted, "predicted")
    present = any(tool == tool_name for tool, _ in pred)
    return {"tool_name": tool_name, "present": present}


def compute_all(
    predicted: Sequence[ToolCallRecord],
    reference: Sequence[ToolCallRecord] | None,
    *,
    single_tool_names: Sequence[str] = (),
) -> dict[str, object]:
    """Compute every trajectory metric.

    When ``reference`` is None, reference-based metrics are reported as None.

    Always-on fields: ``tool_call_count``.
    """
    result: dict[str, object] = {
        "tool_call_count": len(predicted),
    }
    if reference is None:
        result.update(
            exact_match=None,
            in_order_match=None,
            any_order_match=None,
            precision=None,
            recall=None,
        )
    else:
        result.update(
            exact_match=trajectory_exact_match(predicted, reference),
            in_order_match=trajectory_in_order_match(predicted, reference),
            any_order_match=trajectory_any_order_match(predicted, reference),
            precision=trajectory_precision(predicted, reference),
            recall=trajectory_recall(predicted, reference),
        )
    if single_tool_names:
        # When multiple tool names requested, emit a dict keyed by tool name.
        result["single_tool_use"] = {name: single_tool_use(predicted, name) for name in single_tool_names}
    else:
        result["single_tool_use"] = None
    return result


__all__ = [
    "ToolCallRecord",
    "TrajectoryRecordError",
    "compute_all",
    "single_tool_use",
    "trajectory_any_order_match",
    "trajectory_exact_match",
    "trajectory_in_order_match",
    "trajectory_precision",
    "trajectory_recall",
]
