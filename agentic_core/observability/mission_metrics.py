"""
L6 Observability: Mission Metrics

Provides metrics collection for mission controller operations.
"""
from __future__ import annotations
from typing import Any, Dict, Optional
import logging

Logger = logging.getLogger(__name__)


class MissionMetrics:
    """Collects and reports mission execution metrics."""

    def __init__(self):
        self.metrics: Dict[str, Any] = {}
        self.counters: Dict[str, int] = {}

    def record(self, name: str, value: Any) -> None:
        """Record a metric value."""
        self.metrics[name] = value

    def increment(self, name: str, amount: int = 1) -> None:
        """Increment a counter."""
        self.counters[name] = self.counters.get(name, 0) + amount

    def get_all(self) -> Dict[str, Any]:
        """Get all metrics."""
        return {**self.metrics, **self.counters}


_metrics_instance: Optional[MissionMetrics] = None


def get_metrics() -> MissionMetrics:
    """Get or create the global metrics instance."""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = MissionMetrics()
    return _metrics_instance
