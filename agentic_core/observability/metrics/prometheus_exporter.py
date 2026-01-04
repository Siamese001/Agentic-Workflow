"""
Prometheus Metrics Export Module

Provides Prometheus-compatible metrics for healing invocation, entropy, and system health.
Enables alerting on degradation and proactive monitoring.
"""

from __future__ import annotations
from typing import Dict, Any, Optional
from datetime import datetime
import threading


class Counter:
    """Simple counter metric."""
    
    def __init__(self, name: str, description: str, labels: Optional[list] = None):
        """Initialize counter."""
        self.name = name
        self.description = description
        self.labels = labels or []
        self.values: Dict[str, int] = {}
        self._lock = threading.Lock()
    
    def inc(self, amount: int = 1, **label_values) -> None:
        """Increment counter."""
        with self._lock:
            key = self._make_key(label_values)
            self.values[key] = self.values.get(key, 0) + amount
    
    def _make_key(self, label_values: Dict) -> str:
        """Create key from label values."""
        return ','.join(f'{k}={v}' for k, v in sorted(label_values.items()))
    
    def get_value(self, **label_values) -> int:
        """Get counter value."""
        with self._lock:
            key = self._make_key(label_values)
            return self.values.get(key, 0)


class Gauge:
    """Simple gauge metric."""
    
    def __init__(self, name: str, description: str, labels: Optional[list] = None):
        """Initialize gauge."""
        self.name = name
        self.description = description
        self.labels = labels or []
        self.values: Dict[str, float] = {}
        self._lock = threading.Lock()
    
    def set(self, value: float, **label_values) -> None:
        """Set gauge value."""
        with self._lock:
            key = self._make_key(label_values)
            self.values[key] = value
    
    def inc(self, amount: float = 1.0, **label_values) -> None:
        """Increment gauge."""
        with self._lock:
            key = self._make_key(label_values)
            self.values[key] = self.values.get(key, 0.0) + amount
    
    def dec(self, amount: float = 1.0, **label_values) -> None:
        """Decrement gauge."""
        with self._lock:
            key = self._make_key(label_values)
            self.values[key] = self.values.get(key, 0.0) - amount
    
    def _make_key(self, label_values: Dict) -> str:
        """Create key from label values."""
        return ','.join(f'{k}={v}' for k, v in sorted(label_values.items()))
    
    def get_value(self, **label_values) -> float:
        """Get gauge value."""
        with self._lock:
            key = self._make_key(label_values)
            return self.values.get(key, 0.0)


class PrometheusRegistry:
    """Registry for Prometheus metrics."""
    
    def __init__(self):
        """Initialize registry."""
        self.metrics: Dict[str, Any] = {}
        self._lock = threading.Lock()
    
    def register_counter(self, name: str, description: str, labels: Optional[list] = None) -> Counter:
        """Register counter metric."""
        with self._lock:
            counter = Counter(name, description, labels)
            self.metrics[name] = counter
            return counter
    
    def register_gauge(self, name: str, description: str, labels: Optional[list] = None) -> Gauge:
        """Register gauge metric."""
        with self._lock:
            gauge = Gauge(name, description, labels)
            self.metrics[name] = gauge
            return gauge
    
    def get_metric(self, name: str) -> Optional[Any]:
        """Get metric by name."""
        with self._lock:
            return self.metrics.get(name)
    
    def export_text(self) -> str:
        """Export metrics in Prometheus text format."""
        lines = []
        with self._lock:
            for name, metric in self.metrics.items():
                lines.append(f'# HELP {name} {metric.description}')
                lines.append(f'# TYPE {name} counter' if isinstance(metric, Counter) else f'# TYPE {name} gauge')
                
                if isinstance(metric, (Counter, Gauge)):
                    for key, value in metric.values.items():
                        if key:
                            lines.append(f'{name}{{{key}}} {value}')
                        else:
                            lines.append(f'{name} {value}')
        
        return '\n'.join(lines)


# Global registry
registry = PrometheusRegistry()

# Healing metrics
healing_calls = registry.register_counter(
    'healing_calls_total',
    'Total healing invocations',
    labels=['agent']
)

healing_successes = registry.register_counter(
    'healing_successes_total',
    'Successful healing operations',
    labels=['agent']
)

healing_failures = registry.register_counter(
    'healing_failures_total',
    'Failed healing operations',
    labels=['agent']
)

# Invocation metrics
invocation_ratio = registry.register_gauge(
    'healing_invocation_ratio',
    'Healing invocation percentage (0-100)'
)

agent_activations = registry.register_counter(
    'agent_activations_total',
    'Total agent activations',
    labels=['agent']
)

# System metrics
system_entropy = registry.register_gauge(
    'system_entropy',
    'Current Shannon entropy of layer activation'
)

chain_depth = registry.register_gauge(
    'healing_chain_depth',
    'Current healing chain depth'
)

cycle_detections = registry.register_counter(
    'cycle_detections_total',
    'Cycle detections in healing chain'
)

depth_limit_hits = registry.register_counter(
    'depth_limit_hits_total',
    'Depth limit hits in healing chain'
)


def update_invocation_ratio(healing_count: int, total_count: int) -> None:
    """Update invocation ratio metric."""
    if total_count > 0:
        ratio = (healing_count / total_count) * 100
        invocation_ratio.set(ratio)


def update_system_entropy(entropy_value: float) -> None:
    """Update system entropy metric."""
    system_entropy.set(entropy_value)


def update_chain_depth(depth: int) -> None:
    """Update chain depth metric."""
    chain_depth.set(float(depth))


def export_metrics() -> str:
    """Export all metrics in Prometheus format."""
    return registry.export_text()
