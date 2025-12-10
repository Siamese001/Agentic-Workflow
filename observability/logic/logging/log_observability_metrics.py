"""
log_observability_metrics.py - Metrics Module

Domain: logging
Generated: 2025-12-07T12:07:59.844921
"""

import logging
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class Metric:
    """A single metric."""
    name: str
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class LogObservabilityMetrics:
    """Metrics collector for logging domain."""

    def __init__(self, config: Optional[Dict[str, object]] = None):
        self.config = config or {}
        self.metrics: Dict[str, List[Metric]] = defaultdict(list)
        logger.info(f"Initialized {self.__class__.__name__}")

    def record(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Record a metric."""
        metric = Metric(name=name, value=value, labels=labels or {})
        self.metrics[name].append(metric)
        logger.debug(f"Recorded metric {name}={value}")

    def get_metrics(self, name: Optional[str] = None) -> List[Metric]:
        """Get recorded metrics."""
        if name:
            return self.metrics.get(name, [])
        return [m for metrics in self.metrics.values() for m in metrics]

    def get_latest(self, name: str) -> Optional[Metric]:
        """Get latest metric value."""
        metrics = self.metrics.get(name, [])
        return metrics[-1] if metrics else None

    def clear(self, name: Optional[str] = None) -> None:
        """Clear metrics."""
        if name:
            self.metrics.pop(name, None)
        else:
            self.metrics.clear()


# Global instance
_collector = LogObservabilityMetrics()


def record_metric(name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
    """Record a metric to global collector."""
    _collector.record(name, value, labels)


def get_metrics(name: Optional[str] = None) -> List[Metric]:
    """Get metrics from global collector."""
    return _collector.get_metrics(name)
