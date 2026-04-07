"""OpenTelemetry Telemetry Store - Bridges OTel spans to System Learning.

Phase 2: TelemetryConsumer integration with OpenTelemetry.
Provides a TelemetryStore implementation that reads from OpenTelemetry spans.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_records_telemetry_event,
    record_execution_trace,
)
from system_learning.types.telemetry_store_protocol import TelemetryStoreProtocol

logger = logging.getLogger(__name__)


class OpenTelemetrySpanStore(TelemetryStoreProtocol):
    """Telemetry store backed by OpenTelemetry span data.

    Implements TelemetryStoreProtocol to provide seamless integration
    between OpenTelemetry spans and the System Learning telemetry pipeline.

    This store:
    1. Retrieves completed spans from OpenTelemetryTracingAdapter
    2. Converts spans to telemetry events for consumption
    3. Provides time-window based querying for meta-learning analysis

    Attributes
    ----------
    _span_buffer : list[dict[str, Any]]
        Buffer of span data awaiting consumption
    _max_buffer_size : int
        Maximum spans to keep in memory (prevents unbounded growth)
    """

    def __init__(self, max_buffer_size: int = 10000):
        """Initialize the OpenTelemetry span store.

        Parameters
        ----------
        max_buffer_size : int
            Maximum number of spans to retain in memory buffer.
            Older spans are evicted when limit exceeded.
        """
        self._span_buffer: list[dict[str, Any]] = []
        self._max_buffer_size = max_buffer_size

        record_execution_trace("opentelemetry_span_store", "opentelemetry_span_store_init")

    def ingest_spans(self, spans: list[dict[str, Any]]) -> int:
        """Ingest OpenTelemetry spans into the store.

        Called by OpenTelemetryTracingAdapter when spans are completed.

        Parameters
        ----------
        spans : list[dict[str, Any]]
            List of span dictionaries from OpenTelemetry

        Returns
        -------
        int
            Number of spans ingested
        """
        if not spans:
            return 0

        # Add spans to buffer
        self._span_buffer.extend(spans)

        # Evict oldest spans if buffer exceeds max size
        if len(self._span_buffer) > self._max_buffer_size:
            evicted_count = len(self._span_buffer) - self._max_buffer_size
            self._span_buffer = self._span_buffer[-self._max_buffer_size:]
            logger.debug(f"Evicted {evicted_count} old spans from buffer")

        ingested = len(spans)
        _emit_records_telemetry_event(
            "opentelemetry_span_store", "L4_STATE", "span_ingestion",
            ingested_count=ingested,
            buffer_size=len(self._span_buffer),
        )

        return ingested

    def read_events(
        self,
        window_start_utc: int,
        window_end_utc: int,
    ) -> tuple[tuple[int, str, bytes], ...]:
        """Read telemetry events within time window.

        Implements TelemetryStoreProtocol.read_events.

        Parameters
        ----------
        window_start_utc : int
            Start of window (Unix timestamp in milliseconds)
        window_end_utc : int
            End of window (Unix timestamp in milliseconds)

        Returns
        -------
        tuple[tuple[int, str, bytes], ...]
            Events as (ts_utc, kind, payload_bytes)
        """
        events = []

        for span in self._span_buffer:
            ts_utc = span.get("ts_utc", 0)

            # Filter by time window
            if window_start_utc <= ts_utc <= window_end_utc:
                kind = span.get("kind", "unknown")

                # Serialize span data as payload
                payload = {
                    "trace_id": span.get("trace_id", ""),
                    "span_id": span.get("span_id", ""),
                    "parent_span_id": span.get("parent_span_id", ""),
                    "name": span.get("name", ""),
                    "status": span.get("status", ""),
                    "duration_ms": span.get("duration_ms", 0),
                    "layer": span.get("layer", ""),
                    "component": span.get("component", ""),
                    "attributes": span.get("attributes", {}),
                }
                payload_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")

                events.append((ts_utc, kind, payload_bytes))

        _emit_records_telemetry_event(
            "opentelemetry_span_store", "L4_STATE", "read_events",
            window_start=window_start_utc,
            window_end=window_end_utc,
            events_returned=len(events),
        )

        return tuple(events)

    def get_span_count(self) -> int:
        """Get current number of spans in buffer.

        Returns
        -------
        int
            Number of spans in buffer
        """
        return len(self._span_buffer)

    def clear_buffer(self) -> int:
        """Clear all spans from buffer.

        Returns
        -------
        int
            Number of spans cleared
        """
        count = len(self._span_buffer)
        self._span_buffer.clear()
        return count

    def get_latest_spans(self, count: int = 100) -> list[dict[str, Any]]:
        """Get the most recent spans from buffer.

        Parameters
        ----------
        count : int
            Number of spans to return

        Returns
        -------
        list[dict[str, Any]]
            List of latest span dictionaries
        """
        return self._span_buffer[-count:] if self._span_buffer else []


def create_otel_telemetry_store(max_buffer_size: int = 10000) -> OpenTelemetrySpanStore:
    """Factory function to create OpenTelemetry telemetry store.

    Parameters
    ----------
    max_buffer_size : int
        Maximum spans to retain in memory

    Returns
    -------
    OpenTelemetrySpanStore
        Configured telemetry store instance
    """
    return OpenTelemetrySpanStore(max_buffer_size=max_buffer_size)
