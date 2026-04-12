"""Metrics mixin for base agents."""

from __future__ import annotations

from typing import Any, Protocol


class MetricsProtocol(Protocol):
    """Protocol for metrics collection."""

    def record_metric(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        """Record a metric value."""
        ...

    def get_metrics(self) -> dict[str, Any]:
        """Get all recorded metrics."""
        ...


class MetricsMixin:
    """Mixin providing metrics collection capabilities."""

    def __init__(self) -> None:
        self._metrics: dict[str, list[tuple[float, dict[str, str]]]] = {}

    def record_metric(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record a metric value with optional labels."""
        if name not in self._metrics:
            self._metrics[name] = []
        self._metrics[name].append((value, labels or {}))

    def get_metrics(self) -> dict[str, Any]:
        """Get all recorded metrics."""
        return {
            name: {
                "count": len(values),
                "avg": sum(v[0] for v in values) / len(values) if values else 0,
                "values": values,
            }
            for name, values in self._metrics.items()
        }


__all__ = ["MetricsMixin", "MetricsProtocol"]
