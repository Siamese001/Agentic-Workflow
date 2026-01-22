"""
metric_config.py - Metrics Module

Domain: metrics
Generated: 2025-12-07T12:07:59.847509
"""

import logging
import time

logger = logging.getLogger(__name__)


@dataclass
class Metric:
    """A single metric."""

    name: str
    value: float
    labels: dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class MetricConfig:
    """Metrics collector for metrics domain."""

    def __init__(self, config: dict[str, object] | None = None):
        self.config = config or {}
        self.metrics: dict[str, list[Metric]] = defaultdict(list)
        logger.info(f"Initialized {self.__class__.__name__}")

    def record(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        """Record a metric."""
        metric = Metric(name=name, value=value, labels=labels or {})
        self.metrics[name].append(metric)
        logger.debug(f"Recorded metric {name}={value}")

    def get_metrics(self, name: str | None = None) -> list[Metric]:
        """Get recorded metrics."""
        if name:
            return self.metrics.get(name, [])
        return [m for metrics in self.metrics.values() for m in metrics]

    def get_latest(self, name: str) -> Metric | None:
        """Get latest metric value."""
        metrics = self.metrics.get(name, [])
        return metrics[-1] if metrics else None

    def clear(self, name: str | None = None) -> None:
        """Clear metrics."""
        if name:
            self.metrics.pop(name, None)
        else:
            self.metrics.clear()


# Global instance
_collector = MetricConfig()


def record_metric(name: str, value: float, labels: dict[str, str] | None = None) -> None:
    """Record a metric to global collector."""
    _collector.record(name, value, labels)


def get_metrics(name: str | None = None) -> list[Metric]:
    """Get metrics from global collector."""
    return _collector.get_metrics(name)