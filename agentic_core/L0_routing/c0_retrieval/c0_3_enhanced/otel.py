"""Phase 7 — OTEL span emit helpers.

The pipeline emits 7 spans: anchor_extract, anchor_resolve, plan, traverse,
gate, contradiction_scan, emit. We never depend on a real OTEL SDK at import
time; the recorder is a small protocol that can be wired to a real tracer or
left as a no-op for tests.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, MutableMapping, Protocol


class C0GraphSpan(str, Enum):
    ANCHOR_EXTRACT = "c0.graph.anchor_extract"
    ANCHOR_RESOLVE = "c0.graph.anchor_resolve"
    PLAN = "c0.graph.plan"
    TRAVERSE = "c0.graph.traverse"
    GATE = "c0.graph.gate"
    CONTRADICTION_SCAN = "c0.graph.contradiction_scan"
    EMIT = "c0.graph.emit"


@dataclass
class _SpanRecord:
    name: C0GraphSpan
    attributes: MutableMapping[str, Any] = field(default_factory=dict)
    start_ns: int = 0
    end_ns: int = 0


class GraphSpanRecorder(Protocol):
    def start(self, name: C0GraphSpan, attributes: Mapping[str, Any]) -> object: ...
    def end(self, span: object, attributes: Mapping[str, Any] | None = None) -> None: ...
    def list_spans(self) -> tuple[_SpanRecord, ...]: ...


class NullSpanRecorder:
    """Default recorder — captures spans in memory for tests / replay.

    Importantly, it never tries to import an OTEL SDK. A real OTEL adapter
    can wrap this and forward to ``opentelemetry.trace`` if available.
    """

    def __init__(self) -> None:
        self._spans: list[_SpanRecord] = []

    def start(self, name: C0GraphSpan, attributes: Mapping[str, Any]) -> _SpanRecord:
        record = _SpanRecord(
            name=name,
            attributes=dict(attributes),
            start_ns=time.perf_counter_ns(),
        )
        self._spans.append(record)
        return record

    def end(self, span: object, attributes: Mapping[str, Any] | None = None) -> None:
        if not isinstance(span, _SpanRecord):
            return
        span.end_ns = time.perf_counter_ns()
        if attributes:
            span.attributes.update(attributes)

    def list_spans(self) -> tuple[_SpanRecord, ...]:
        return tuple(self._spans)


__all__ = ["C0GraphSpan", "GraphSpanRecorder", "NullSpanRecorder"]
