"""ADG Runtime Tracer — Runtime execution tracing for ADG."""

from __future__ import annotations

from typing import Any


class RuntimeTracer:
    """Traces runtime execution for ADG edge recording."""

    def __init__(self) -> None:
        self.traces: list[dict[str, Any]] = []

    def record_trace(self, src: str, dst: str, relation: str) -> None:
        """Record a runtime trace."""
        self.traces.append({"src": src, "dst": dst, "relation": relation})

    def get_traces(self) -> list[dict[str, Any]]:
        """Get all recorded traces."""
        return self.traces.copy()
