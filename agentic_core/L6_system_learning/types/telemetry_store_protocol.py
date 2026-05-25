"""Telemetry Store Protocol for OpenTelemetry span integration.

Defines the interface for storing and retrieving telemetry data
from OpenTelemetry spans for system learning analysis.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class TelemetryStoreProtocol(Protocol):
    """Protocol for telemetry store implementations.

    Provides methods for storing and retrieving telemetry data
    from OpenTelemetry spans for analysis.
    """

    def store_span_data(
        self,
        span_data: list[dict[str, any]],
        timestamp_utc: int,
    ) -> bool:
        """Store span data for telemetry analysis.

        Args:
            span_data: List of span dictionaries
            timestamp_utc: Storage timestamp in milliseconds

        Returns:
            True if stored successfully, False on failure
        """
        ...

    def store_span_metrics(
        self,
        metrics: dict[str, any],
        timestamp_utc: int,
    ) -> bool:
        """Store span metrics for telemetry analysis.

        Args:
            metrics: Span metrics dictionary
            timestamp_utc: Storage timestamp in milliseconds

        Returns:
            True if stored successfully, False on failure
        """
        ...

    def query_spans_by_time_range(
        self,
        start_utc: int,
        end_utc: int,
        limit: int = 100,
    ) -> list[dict[str, any]]:
        """Query spans within a time range.

        Args:
            start_utc: Start timestamp in milliseconds
            end_utc: End timestamp in milliseconds
            limit: Maximum number of results

        Returns:
            List of span data within time range
        """
        ...

    def query_metrics_by_time_range(
        self,
        start_utc: int,
        end_utc: int,
    ) -> list[dict[str, any]]:
        """Query metrics within a time range.

        Args:
            start_utc: Start timestamp in milliseconds
            end_utc: End timestamp in milliseconds

        Returns:
            List of metrics within time range
        """
        ...

    def get_latest_span_count(self) -> int:
        """Get the count of latest spans.

        Returns:
            Number of spans in latest batch
        """
        ...

    def cleanup_old_data(self, retention_hours: int = 24) -> int:
        """Clean up old telemetry data.

        Args:
            retention_hours: Data retention period in hours

        Returns:
            Number of records cleaned up
        """
        ...
