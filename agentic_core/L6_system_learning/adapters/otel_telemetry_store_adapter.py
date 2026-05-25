"""OpenTelemetry Telemetry Store Adapter.

Adapter for storing OpenTelemetry span data in the system learning
memory bridge for telemetry analysis and drift detection.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any

from .system_learning_memory_bridge import get_sl_memory_bridge
from tqdm import tqdm

logger = logging.getLogger(__name__)
_MAX_SPANS_PER_BATCH = 50


class OTelTelemetryStoreAdapter:
    """Adapter for storing OpenTelemetry telemetry data.

    Bridges OpenTelemetry span data with the system learning memory
    bridge for persistent storage and analysis.
    """

    def __init__(self, bridge=None):
        """Initialize the adapter.

        Args:
            bridge: Optional system learning memory bridge instance
        """
        self._bridge = bridge or get_sl_memory_bridge()

    def store_span_data(
        self,
        span_data: list[dict[str, Any]],
        timestamp_utc: int,
    ) -> bool:
        """Store span data for telemetry analysis.

        Args:
            span_data: List of span dictionaries
            timestamp_utc: Storage timestamp in milliseconds

        Returns:
            True if stored successfully, False on failure
        """
        if not span_data:
            return False

        try:
            if len(span_data) > _MAX_SPANS_PER_BATCH:
                logger.warning(
                    "[OTelAdapter] Truncating span batch from %d to %d entries",
                    len(span_data),
                    _MAX_SPANS_PER_BATCH,
                )
            stored_count = 0
            skipped_count = 0
            for span in tqdm(span_data[:_MAX_SPANS_PER_BATCH], desc="Processing", unit="item"):
                try:
                    span_json = json.dumps(span, sort_keys=True, separators=(",", ":"))
                except (TypeError, ValueError) as exc:
                    skipped_count += 1
                    logger.debug("[OTelAdapter] Skipping non-serializable span: %s", exc)
                    continue

                success = self._bridge.persist_otel_span(
                    span_id=str(span.get("span_id", "unknown")),
                    trace_id=str(span.get("trace_id", "unknown")),
                    span_name=str(span.get("name", "unknown")),
                    span_data_json=span_json,
                    timestamp_utc=timestamp_utc,
                )

                if success:
                    stored_count += 1

            if skipped_count:
                logger.warning("[OTelAdapter] Skipped %d non-serializable spans", skipped_count)
            logger.debug("[OTelAdapter] Stored %d spans out of %d", stored_count, len(span_data))
            return stored_count > 0

        except AttributeError as exc:
            logger.debug("[OTelAdapter] Bridge missing span persistence method: %s", exc)
            return False

    def store_span_metrics(
        self,
        metrics: dict[str, Any],
        timestamp_utc: int,
    ) -> bool:
        """Store span metrics for telemetry analysis.

        Args:
            metrics: Span metrics dictionary
            timestamp_utc: Storage timestamp in milliseconds

        Returns:
            True if stored successfully, False on failure
        """
        try:
            metrics_json = json.dumps(metrics, sort_keys=True, separators=(",", ":"))

            success = self._bridge.persist_otel_span_metrics(
                metrics_json=metrics_json,
                timestamp_utc=timestamp_utc,
            )

            if success:
                logger.debug("[OTelAdapter] Stored span metrics: total=%s", metrics.get("total_spans", 0))

            return success

        except (AttributeError, TypeError, ValueError) as exc:
            logger.debug("[OTelAdapter] Failed to store span metrics: %s", exc)
            return False

    def query_spans_by_time_range(
        self,
        start_utc: int,
        end_utc: int,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Query spans within a time range.

        Args:
            start_utc: Start timestamp in milliseconds
            end_utc: End timestamp in milliseconds
            limit: Maximum number of results

        Returns:
            List of span data within time range
        """
        # Placeholder implementation - would need query method in bridge
        logger.debug(f"[OTelAdapter] Query spans from {start_utc} to {end_utc} (limit={limit})")
        return []

    def query_metrics_by_time_range(
        self,
        start_utc: int,
        end_utc: int,
    ) -> list[dict[str, Any]]:
        """Query metrics within a time range.

        Args:
            start_utc: Start timestamp in milliseconds
            end_utc: End timestamp in milliseconds

        Returns:
            List of metrics within time range
        """
        # Placeholder implementation - would need query method in bridge
        logger.debug(f"[OTelAdapter] Query metrics from {start_utc} to {end_utc}")
        return []

    def get_latest_span_count(self) -> int:
        """Get the count of latest spans.

        Returns:
            Number of spans in latest batch
        """
        # Placeholder implementation
        return 0

    def cleanup_old_data(self, retention_hours: int = 24) -> int:
        """Clean up old telemetry data.

        Args:
            retention_hours: Data retention period in hours

        Returns:
            Number of records cleaned up
        """
        # Placeholder implementation
        logger.debug(f"[OTelAdapter] Cleanup data older than {retention_hours} hours")
        return 0

    def collect_and_store_current_spans(self) -> bool:
        """Collect and store current OpenTelemetry spans.

        Returns:
            True if collection and storage successful
        """
        try:
            from apps_shared.utils.open_telemetry_tracing_adapter_util import get_tracer

            tracer = get_tracer()
            if not tracer.is_enabled():
                return False

            # Get current spans and metrics
            spans = tracer.get_active_spans()
            metrics = tracer.get_span_metrics()

            timestamp_utc = int(time.time() * 1000)

            # Store spans and metrics
            spans_stored = self.store_span_data(spans, timestamp_utc)
            metrics_stored = self.store_span_metrics(metrics, timestamp_utc)

            return spans_stored or metrics_stored

        except (AttributeError, ImportError, TypeError, ValueError) as exc:
            logger.debug("[OTelAdapter] Failed to collect spans: %s", exc)
            return False


# Create a singleton instance for global access
_otel_adapter_instance: OTelTelemetryStoreAdapter | None = None


def get_otel_adapter() -> OTelTelemetryStoreAdapter:
    """Get the global OTel telemetry store adapter instance.

    Returns:
        OTelTelemetryStoreAdapter instance
    """
    global _otel_adapter_instance
    if _otel_adapter_instance is None:
        _otel_adapter_instance = OTelTelemetryStoreAdapter()
    return _otel_adapter_instance


def collect_otel_telemetry() -> bool:
    """Collect and store current OpenTelemetry telemetry.

    Convenience function for periodic telemetry collection.

    Returns:
        True if collection successful
    """
    adapter = get_otel_adapter()
    return adapter.collect_and_store_current_spans()
