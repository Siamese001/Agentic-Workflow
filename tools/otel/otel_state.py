from __future__ import annotations

import time
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class RuntimeMetrics:
    """Mutable in-memory runtime counters for the current MCP process."""

    last_updated: int = field(default_factory=lambda: int(time.time()))
    total_traces: int = 0
    total_spans: int = 0
    error_count: int = 0
    anomaly_count: int = 0

    def mark_error(self) -> None:
        self.error_count += 1

    def record_ingest(self, span_count: int) -> None:
        self.total_traces += 1
        self.total_spans += span_count
        self.last_updated = int(time.time())

    def to_dict(self) -> dict[str, Any]:
        return {
            "last_updated": self.last_updated,
            "total_traces": self.total_traces,
            "total_spans": self.total_spans,
            "error_count": self.error_count,
            "anomaly_count": self.anomaly_count,
        }


class TraceCache:
    """Bounded in-memory LRU cache for recently used traces."""

    def __init__(self, max_traces: int) -> None:
        self._max_traces = max_traces
        self._cache: OrderedDict[str, dict[str, Any]] = OrderedDict()

    def __contains__(self, trace_id: str) -> bool:
        return trace_id in self._cache

    def __len__(self) -> int:
        return len(self._cache)

    def get(self, trace_id: str) -> dict[str, Any] | None:
        payload = self._cache.get(trace_id)
        if payload is not None:
            self._cache.move_to_end(trace_id)
        return payload

    def put(self, trace_id: str, payload: dict[str, Any]) -> None:
        self._cache[trace_id] = payload
        self._cache.move_to_end(trace_id)
        while len(self._cache) > self._max_traces:
            self._cache.popitem(last=False)

    def items(self):
        return self._cache.items()

    def values(self):
        return self._cache.values()
