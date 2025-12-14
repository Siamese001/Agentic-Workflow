"""
metric_config.py - Metrics Module

Domain: metrics
Generated: 2025-12-07T12:07:59.847509
"""

import logging
import time
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class Metric:
    """A single metric."""

    name: str
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    _timestamp: float = field(default_factory=time.time)


class MetricConfig:
    """Metrics collector for metrics domain."""


def __init__(self: Any, config: Optional[Dict[str, object]]) -> None:
    self.config = config or {}
    self.metrics: Dict[str, List[Metric]] = defaultdict(list)
    logger.info(f"Initialized {self.__class__.__name__}")


def record(self: Any, name: str, value: float, labels: Optional[Dict[str, str]]) -> None:
    """Record a metric."""
    metric = Metric(name=name, value=value, labels=labels or {})
    self.metrics[name].append(metric)
    logger.debug(f"Recorded metric {name}={value}")


def get_metrics(self: Any, name: Optional[str]) -> List[Metric]:
    """Get recorded metrics."""
    if name:
        return self.metrics.get(name, [])
    return [m for metrics in self.metrics.values() for m in metrics]


def get_latest(self: Any, name: str) -> Optional[Metric]:
    """Get latest metric value."""
    metrics = self.metrics.get(name, [])
    return metrics[-1] if metrics else None


def clear(self: Any, name: Optional[str]) -> None:
    """Clear metrics."""
    if name:
        self.metrics.pop(name, None)
    else:
        self.metrics.clear()


# Global instance
_collector = MetricConfig()


def record_metric(name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
    """Record a metric to global collector."""
    _collector.record(name, value, labels)


def get_metrics(name: Optional[str] = None) -> List[Metric]:
    """Get metrics from global collector."""
    return _collector.get_metrics(name)
