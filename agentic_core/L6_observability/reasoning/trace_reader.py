"""C2 Trace Reader - L6 read surfaces for execution traces.

10C-REQ-128: L6 Read Surfaces execution traces exit dispositions telemetry
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from enum import Enum, auto


class ExitDisposition(Enum):
    """Exit disposition types."""

    ALLOW = auto()
    DENY = auto()
    ESCALATE = auto()
    COMMIT = auto()


@dataclass
class ExecutionTrace:
    """Execution trace record."""

    trace_id: str
    request_id: str
    layer_path: list[str]
    start_time: float
    end_time: float
    exit_disposition: ExitDisposition
    telemetry: dict[str, Any]


class TraceReader:
    """C2 L6 Trace Reader.

    10C-REQ-128: Read surfaces for execution traces, exit dispositions, telemetry.
    """

    def __init__(self) -> None:
        self._traces: dict[str, ExecutionTrace] = {}
        self._disposition_counts: dict[ExitDisposition, int] = {disp: 0 for disp in ExitDisposition}

    def register_trace(self, trace: ExecutionTrace) -> None:
        """Register execution trace for L6 read surface."""
        self._traces[trace.trace_id] = trace
        self._disposition_counts[trace.exit_disposition] += 1

    def get_trace(self, trace_id: str) -> ExecutionTrace | None:
        """Get trace by ID."""
        return self._traces.get(trace_id)

    def query_by_disposition(
        self,
        disposition: ExitDisposition,
        limit: int = 100,
    ) -> list[ExecutionTrace]:
        """Query traces by exit disposition."""
        results = [t for t in self._traces.values() if t.exit_disposition == disposition]
        return results[:limit]

    def get_disposition_stats(self) -> dict[str, int]:
        """Get exit disposition statistics."""
        return {disp.name: count for disp, count in self._disposition_counts.items()}

    def get_telemetry_aggregate(
        self,
        metric_name: str,
        trace_ids: list[str] | None = None,
    ) -> dict[str, float]:
        """Aggregate telemetry metric across traces."""
        values: list[float] = []

        traces = (
            self._traces.values()
            if trace_ids is None
            else [self._traces[tid] for tid in trace_ids if tid in self._traces]
        )

        for trace in traces:
            if metric_name in trace.telemetry:
                val = trace.telemetry[metric_name]
                if isinstance(val, (int, float)):
                    values.append(float(val))

        if not values:
            return {"count": 0, "min": 0, "max": 0, "avg": 0}

        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
        }
