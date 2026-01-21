"""
L6 Observability: Mission Metrics

Provides metrics collection for mission controller operations.
"""

from __future__ import annotations

import logging
from typing import Any

Logger = logging.getLogger(__name__)


class MissionMetrics:
    """Collects and reports mission execution metrics."""

    def __init__(self):
        self.metrics: dict[str, Any] = {}
        self.counters: dict[str, int] = {}

    def record(self, name: str, value: Any) -> None:
        """Record a metric value."""
        self.metrics[name] = value

    def increment(self, name: str, amount: int = 1) -> None:
        """Increment a counter."""
        self.counters[name] = self.counters.get(name, 0) + amount

    def get_all(self) -> dict[str, Any]:
        """Get all metrics."""
        return {**self.metrics, **self.counters}


_metrics_instance: MissionMetrics | None = None


def get_metrics() -> MissionMetrics:
    """Get or create the global metrics instance."""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = MissionMetrics()
    return _metrics_instance
