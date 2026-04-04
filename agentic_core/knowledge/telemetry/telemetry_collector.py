"""Telemetry Collector.

Structured logging and event collection for the RAG pipeline.
"""

import json
import logging
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
)

log = logging.getLogger(__name__)


class EventType(Enum):
    """Types of telemetry events."""
    QUERY_START = "query_start"
    QUERY_END = "query_end"
    CACHE_HIT = "cache_hit"
    CACHE_MISS = "cache_miss"
    RETRIEVAL_START = "retrieval_start"
    RETRIEVAL_END = "retrieval_end"
    RERANK_START = "rerank_start"
    RERANK_END = "rerank_end"
    GENERATION_START = "generation_start"
    GENERATION_END = "generation_end"
    ERROR = "error"


@dataclass
class TelemetryEvent:
    """A telemetry event."""
    event_type: EventType
    query_id: str
    timestamp: float = field(default_factory=time.time)
    duration_ms: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class TelemetryCollector:
    """Collects and manages telemetry events.

    The TelemetryCollector provides structured logging and event
    collection for monitoring RAG pipeline performance.
    """

    def __init__(self, max_events: int = 10000):
        """Initialize the telemetry collector.

        Args:
            max_events: Maximum events to retain in memory
        """
        self.max_events = max_events
        self._events: list[TelemetryEvent] = []

        log.info(f"TelemetryCollector initialized (max_events={max_events})")

    def record_event(
        self,
        event_type: EventType,
        query_id: str,
        duration_ms: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> TelemetryEvent:
        """Record a telemetry event.

        Args:
            event_type: Type of event
            query_id: Query identifier
            duration_ms: Optional duration in milliseconds
            metadata: Optional event metadata

        Returns:
            Recorded TelemetryEvent
        """
        trace_id = f"telemetry_{query_id}"
        _emit_records_execution_trace(
            trace_id, LayerSegment.L1_REASONING, "TelemetryCollector.record_event"
        )

        event = TelemetryEvent(
            event_type=event_type,
            query_id=query_id,
            duration_ms=duration_ms,
            metadata=metadata or {},
        )

        self._events.append(event)

        # Trim if exceeding max
        if len(self._events) > self.max_events:
            self._events = self._events[-self.max_events:]

        return event

    def record_start(self, event_type: EventType, query_id: str) -> float:
        """Record start of an operation.

        Args:
            event_type: Type of event
            query_id: Query identifier

        Returns:
            Start timestamp
        """
        self.record_event(event_type, query_id)
        return time.time()

    def record_end(
        self,
        event_type: EventType,
        query_id: str,
        start_time: float,
        metadata: dict[str, Any] | None = None,
    ) -> TelemetryEvent:
        """Record end of an operation.

        Args:
            event_type: Type of event
            query_id: Query identifier
            start_time: Start timestamp from record_start
            metadata: Optional metadata

        Returns:
            Recorded TelemetryEvent
        """
        duration_ms = (time.time() - start_time) * 1000
        return self.record_event(
            event_type=event_type,
            query_id=query_id,
            duration_ms=duration_ms,
            metadata=metadata,
        )

    def get_events(
        self,
        event_type: EventType | None = None,
        query_id: str | None = None,
        limit: int = 100,
    ) -> list[TelemetryEvent]:
        """Get filtered events.

        Args:
            event_type: Optional filter by type
            query_id: Optional filter by query ID
            limit: Maximum events to return

        Returns:
            List of matching events
        """
        filtered = self._events

        if event_type:
            filtered = [e for e in filtered if e.event_type == event_type]

        if query_id:
            filtered = [e for e in filtered if e.query_id == query_id]

        return filtered[-limit:]

    def export_events(self, format: str = "json") -> str:
        """Export events as string.

        Args:
            format: Export format (json, csv)

        Returns:
            Exported events string
        """
        if format == "json":
            events_dict = [asdict(e) for e in self._events]
            return json.dumps(events_dict, default=str, indent=2)

        return ""

    def clear(self) -> int:
        """Clear all events.

        Returns:
            Number of events cleared
        """
        count = len(self._events)
        self._events.clear()
        return count


# Global instance
_global_collector: TelemetryCollector | None = None


def get_telemetry_collector() -> TelemetryCollector:
    """Get or create the global telemetry collector."""
    global _global_collector
    if _global_collector is None:
        _global_collector = TelemetryCollector()
    return _global_collector


def record_event(
    event_type: EventType,
    query_id: str,
    duration_ms: float | None = None,
    metadata: dict[str, Any] | None = None,
) -> TelemetryEvent:
    """Convenience function to record event."""
    return get_telemetry_collector().record_event(
        event_type, query_id, duration_ms, metadata
    )
