from __future__ import annotations

from collections import defaultdict
from threading import Lock
from typing import Any

_CAPTURED_METRICS: list[tuple[str, str, str]] = []
_CAPTURED_METRICS_LOCK = Lock()


def _normalize_metric_fields(trace_id: Any, lane: Any, metric_name: Any) -> tuple[str, str, str]:
    return (str(trace_id or ""), str(lane or ""), str(metric_name or ""))


def _emit_captures_evaluation_metric(trace_id: str, lane: str, metric_name: str) -> None:
    normalized = _normalize_metric_fields(trace_id, lane, metric_name)
    with _CAPTURED_METRICS_LOCK:
        _CAPTURED_METRICS.append(normalized)
        overflow = len(_CAPTURED_METRICS) - 10_000
        if overflow > 0:
            del _CAPTURED_METRICS[:overflow]


def get_captured_evaluation_metrics() -> list[tuple[str, str, str]]:
    with _CAPTURED_METRICS_LOCK:
        return list(_CAPTURED_METRICS)


def summarize_captured_evaluation_metrics() -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = defaultdict(dict)
    with _CAPTURED_METRICS_LOCK:
        for _trace_id, lane, metric_name in _CAPTURED_METRICS:
            lane_metrics = summary.setdefault(lane, {})
            lane_metrics[metric_name] = lane_metrics.get(metric_name, 0) + 1
    return {lane: dict(metrics) for lane, metrics in summary.items()}


def reset_captured_evaluation_metrics() -> None:
    with _CAPTURED_METRICS_LOCK:
        _CAPTURED_METRICS.clear()
