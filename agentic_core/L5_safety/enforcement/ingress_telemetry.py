"""Lightweight ingress telemetry — rejection / latency counters.

Closes gap G-11: the ingress gate was silent. This module exposes a small
counter surface (``IngressMetrics``) that the gate / adapters can update on
every outcome. L6 ``observability_recorder`` MAY wrap an instance and forward
to the real metric sink; the default is an in-memory counter that tests can
inspect.

Layer authority: L5 (policy plane) — in-process counters only; no network,
no durable writes.
"""

from __future__ import annotations

import threading
import time
from collections import Counter
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable


@runtime_checkable
class IngressMetricsSink(Protocol):
    """Protocol for a metric sink — allows L6 / OTEL to plug in later."""

    def incr(self, metric: str, *, labels: dict[str, str] | None = None) -> None: ...

    def observe(self, metric: str, value: float, *, labels: dict[str, str] | None = None) -> None: ...


@dataclass
class InMemoryMetricsSink:
    """Default thread-safe counter sink for tests and smoke runs."""

    counters: Counter[tuple[str, tuple[tuple[str, str], ...]]] = field(default_factory=Counter)
    observations: dict[tuple[str, tuple[tuple[str, str], ...]], list[float]] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def incr(self, metric: str, *, labels: dict[str, str] | None = None) -> None:
        key = (metric, self._label_key(labels))
        with self._lock:
            self.counters[key] += 1

    def observe(self, metric: str, value: float, *, labels: dict[str, str] | None = None) -> None:
        key = (metric, self._label_key(labels))
        with self._lock:
            self.observations.setdefault(key, []).append(float(value))

    def get(self, metric: str, labels: dict[str, str] | None = None) -> int:
        return int(self.counters.get((metric, self._label_key(labels)), 0))

    @staticmethod
    def _label_key(labels: dict[str, str] | None) -> tuple[tuple[str, str], ...]:
        if not labels:
            return ()
        return tuple(sorted((str(k), str(v)) for k, v in labels.items()))


class IngressMetrics:
    """Façade the ingress gate and adapters use.

    Canonical metric names::

        ingress_requests_total                  (labels: outcome)
        ingress_rejections_total                (labels: reason_code, gate_stage)
        ingress_clarifications_total            (labels: reason)
        ingress_latency_ms                      (labels: outcome)   [observation]

    Consumers downstream of this module MUST use these exact names to stay
    compatible with the default in-memory sink and any future OTEL adapter.
    """

    def __init__(self, sink: IngressMetricsSink | None = None) -> None:
        self._sink: IngressMetricsSink = sink or InMemoryMetricsSink()

    @property
    def sink(self) -> IngressMetricsSink:
        return self._sink

    def record_accepted(self, *, tenant_id: str, latency_ms: float) -> None:
        self._sink.incr("ingress_requests_total", labels={"outcome": "accepted"})
        self._sink.observe(
            "ingress_latency_ms", latency_ms, labels={"outcome": "accepted", "tenant": tenant_id}
        )

    def record_rejection(self, *, reason_code: str, gate_stage: str, latency_ms: float) -> None:
        self._sink.incr("ingress_requests_total", labels={"outcome": "rejected"})
        self._sink.incr(
            "ingress_rejections_total",
            labels={"reason_code": reason_code, "gate_stage": gate_stage},
        )
        self._sink.observe("ingress_latency_ms", latency_ms, labels={"outcome": "rejected"})

    def record_clarification(self, *, reason: str, latency_ms: float) -> None:
        self._sink.incr("ingress_requests_total", labels={"outcome": "clarification"})
        self._sink.incr("ingress_clarifications_total", labels={"reason": reason[:60]})
        self._sink.observe("ingress_latency_ms", latency_ms, labels={"outcome": "clarification"})


# Module-level default metrics instance. Callers may replace the sink by
# calling ``set_default_sink`` at application startup.
_DEFAULT = IngressMetrics()


def default_metrics() -> IngressMetrics:
    return _DEFAULT


def set_default_sink(sink: IngressMetricsSink) -> None:
    global _DEFAULT
    _DEFAULT = IngressMetrics(sink)


def monotonic_ms() -> float:
    return time.monotonic() * 1000.0


__all__ = [
    "InMemoryMetricsSink",
    "IngressMetrics",
    "IngressMetricsSink",
    "default_metrics",
    "monotonic_ms",
    "set_default_sink",
]
