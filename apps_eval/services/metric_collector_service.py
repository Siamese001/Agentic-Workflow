"""
Metric Collector Service — apps_eval

Stub service for collecting evaluation metrics.
Full implementation to be expanded based on usage patterns.
"""

from __future__ import annotations

import logging
from typing import Any

from apps_eval._telemetry import (
    _emit_captures_evaluation_metric,
    _emit_records_telemetry_event,
)

_log = logging.getLogger(__name__)


class MetricCollectorService:
    """Stub service for metric collection."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}
        _emit_records_telemetry_event("p4", "metric_collector", "init")

    def record_metric(self, name: str, value: float, context: dict[str, Any] | None = None) -> None:
        """Record a single metric value."""
        _emit_captures_evaluation_metric("p4", "metric_collector", f"{name}:{value}")
        _log.debug("Recorded metric %s = %f", name, value)

    def get_metrics(self) -> list[dict[str, Any]]:
        """Get collected metrics."""
        return []
