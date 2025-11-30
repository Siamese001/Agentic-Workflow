"""
Metrics Collector Implementation

Provides comprehensive metrics collection and aggregation for monitoring
agentic workflows across the L1-L5 architecture.
"""

from __future__ import annotations

import asyncio
import time
import statistics
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, Union
from enum import Enum
from collections import defaultdict, deque
import json
import threading

from ..tracing.tracer import get_tracer, Span


class MetricType(str, Enum):
    """Types of metrics that can be collected."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    SUMMARY = "summary"


@dataclass
class MetricValue:
    """Individual metric value with metadata."""
    name: str
    value: Union[int, float]
    metric_type: MetricType
    timestamp: float = field(default_factory=time.time)
    labels: Dict[str, str] = field(default_factory=dict)
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "value": self.value,
            "type": self.metric_type.value,
            "timestamp": self.timestamp,
            "labels": self.labels,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
        }


@dataclass
class HistogramBucket:
    """Histogram bucket for value distribution."""
    upper_bound: float
    count: int = 0
    
    def observe(self, value: float) -> None:
        """Add value to bucket if within bounds."""
        if value <= self.upper_bound:
            self.count += 1


@dataclass
class MetricSummary:
    """Summary statistics for a metric."""
    name: str
    metric_type: MetricType
    count: int = 0
    sum: float = 0.0
    min: Optional[float] = None
    max: Optional[float] = None
    avg: float = 0.0
    recent_values: deque = field(default_factory=lambda: deque(maxlen=1000))
    
    def update(self, value: float) -> None:
        """Update summary with new value."""
        self.count += 1
        self.sum += value
        self.recent_values.append(value)
        
        if self.min is None or value < self.min:
            self.min = value
        if self.max is None or value > self.max:
            self.max = value
        
        self.avg = self.sum / self.count
    
    def get_percentile(self, percentile: float) -> float:
        """Calculate percentile of recent values."""
        if not self.recent_values:
            return 0.0
        
        sorted_values = sorted(self.recent_values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]


class MetricsCollector:
    """Comprehensive metrics collection for agentic workflows."""
    
    def __init__(self, service_name: str = "agentic-workflow", max_history: int = 10000):
        self.service_name = service_name
        self.max_history = max_history
        
        # Metric storage
        self.counters: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.gauges: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self.histograms: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
        self.timers: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
        self.summaries: Dict[str, Dict[str, MetricSummary]] = defaultdict(dict)
        
        # Raw metric history
        self.metric_history: List[MetricValue] = []
        self.history_lock = threading.Lock()
        
        # Histogram buckets configuration
        self.default_histogram_buckets = [
            0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 25.0, 50.0, 100.0, 250.0, 500.0, 1000.0, float('inf')
        ]
        
        # Aggregation callbacks
        self.aggregation_callbacks: List[Callable[[List[MetricValue]], None]] = []
        
        # Background collection task
        self._collection_task: Optional[asyncio.Task] = None
        self._running = False
    
    def collect(self, metric_name: str, value: Union[int, float], 
                metric_type: MetricType = MetricType.GAUGE,
                labels: Optional[Dict[str, str]] = None) -> MetricValue:
        """Collect a metric value."""
        labels = labels or {}
        label_key = self._make_label_key(labels)
        
        # Get current trace context
        tracer = get_tracer()
        current_span = tracer.get_current_span()
        
        metric_value = MetricValue(
            name=metric_name,
            value=value,
            metric_type=metric_type,
            labels=labels,
            trace_id=current_span.trace_id if current_span else None,
            span_id=current_span.span_id if current_span else None,
        )
        
        # Store in appropriate metric type
        if metric_type == MetricType.COUNTER:
            self.counters[metric_name][label_key] += int(value)
        elif metric_type == MetricType.GAUGE:
            self.gauges[metric_name][label_key] = float(value)
        elif metric_type == MetricType.HISTOGRAM:
            self.histograms[metric_name][label_key].append(float(value))
        elif metric_type == MetricType.TIMER:
            self.timers[metric_name][label_key].append(float(value))
        elif metric_type == MetricType.SUMMARY:
            if metric_name not in self.summaries or label_key not in self.summaries[metric_name]:
                self.summaries[metric_name][label_key] = MetricSummary(
                    name=metric_name,
                    metric_type=metric_type
                )
            self.summaries[metric_name][label_key].update(float(value))
        
        # Add to history
        with self.history_lock:
            self.metric_history.append(metric_value)
            if len(self.metric_history) > self.max_history:
                self.metric_history.pop(0)
        
        # Trigger aggregation callbacks
        for callback in self.aggregation_callbacks:
            try:
                callback([metric_value])
            except Exception:
                pass  # Ignore callback errors
        
        return metric_value
    
    def increment_counter(self, metric_name: str, value: int = 1, 
                          labels: Optional[Dict[str, str]] = None) -> MetricValue:
        """Increment a counter metric."""
        return self.collect(metric_name, value, MetricType.COUNTER, labels)
    
    def set_gauge(self, metric_name: str, value: float, 
                  labels: Optional[Dict[str, str]] = None) -> MetricValue:
        """Set a gauge metric value."""
        return self.collect(metric_name, value, MetricType.GAUGE, labels)
    
    def observe_histogram(self, metric_name: str, value: float,
                         labels: Optional[Dict[str, str]] = None) -> MetricValue:
        """Observe a histogram metric value."""
        return self.collect(metric_name, value, MetricType.HISTOGRAM, labels)
    
    def record_timer(self, metric_name: str, duration_ms: float,
                     labels: Optional[Dict[str, str]] = None) -> MetricValue:
        """Record a timer metric value."""
        return self.collect(metric_name, duration_ms, MetricType.TIMER, labels)
    
    def time_function(self, metric_name: str, labels: Optional[Dict[str, str]] = None):
        """Decorator to time function execution."""
        def decorator(func):
            if asyncio.iscoroutinefunction(func):
                async def async_wrapper(*args, **kwargs):
                    start_time = time.time()
                    try:
                        result = await func(*args, **kwargs)
                        return result
                    finally:
                        duration_ms = (time.time() - start_time) * 1000
                        self.record_timer(metric_name, duration_ms, labels)
                return async_wrapper
            else:
                def sync_wrapper(*args, **kwargs):
                    start_time = time.time()
                    try:
                        result = func(*args, **kwargs)
                        return result
                    finally:
                        duration_ms = (time.time() - start_time) * 1000
                        self.record_timer(metric_name, duration_ms, labels)
                return sync_wrapper
        return decorator
    
    def get_counter(self, metric_name: str, labels: Optional[Dict[str, str]] = None) -> int:
        """Get counter value."""
        label_key = self._make_label_key(labels or {})
        return self.counters[metric_name][label_key]
    
    def get_gauge(self, metric_name: str, labels: Optional[Dict[str, str]] = None) -> float:
        """Get gauge value."""
        label_key = self._make_label_key(labels or {})
        return self.gauges[metric_name][label_key]
    
    def get_histogram_stats(self, metric_name: str, labels: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Get histogram statistics."""
        label_key = self._make_label_key(labels or {})
        values = self.histograms[metric_name][label_key]
        
        if not values:
            return {"count": 0, "sum": 0.0, "avg": 0.0}
        
        return {
            "count": len(values),
            "sum": sum(values),
            "avg": statistics.mean(values),
            "min": min(values),
            "max": max(values),
            "median": statistics.median(values),
            "percentiles": {
                "50": statistics.median(values),
                "90": self._percentile(values, 0.9),
                "95": self._percentile(values, 0.95),
                "99": self._percentile(values, 0.99),
            }
        }
    
    def get_timer_stats(self, metric_name: str, labels: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Get timer statistics."""
        return self.get_histogram_stats(metric_name, labels)
    
    def get_summary_stats(self, metric_name: str, labels: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Get summary statistics."""
        label_key = self._make_label_key(labels or {})
        summary = self.summaries[metric_name][label_key]
        
        if not summary:
            return {"count": 0, "sum": 0.0, "avg": 0.0}
        
        return {
            "count": summary.count,
            "sum": summary.sum,
            "avg": summary.avg,
            "min": summary.min,
            "max": summary.max,
            "percentiles": {
                "50": summary.get_percentile(50),
                "90": summary.get_percentile(90),
                "95": summary.get_percentile(95),
                "99": summary.get_percentile(99),
            }
        }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all current metric values."""
        result = {
            "counters": {},
            "gauges": {},
            "histograms": {},
            "timers": {},
            "summaries": {},
        }
        
        # Counters
        for metric_name, label_dict in self.counters.items():
            result["counters"][metric_name] = dict(label_dict)
        
        # Gauges
        for metric_name, label_dict in self.gauges.items():
            result["gauges"][metric_name] = dict(label_dict)
        
        # Histograms
        for metric_name, label_dict in self.histograms.items():
            result["histograms"][metric_name] = {
                label_key: self.get_histogram_stats(metric_name, self._parse_label_key(label_key))
                for label_key in label_dict.keys()
            }
        
        # Timers
        for metric_name, label_dict in self.timers.items():
            result["timers"][metric_name] = {
                label_key: self.get_timer_stats(metric_name, self._parse_label_key(label_key))
                for label_key in label_dict.keys()
            }
        
        # Summaries
        for metric_name, label_dict in self.summaries.items():
            result["summaries"][metric_name] = {
                label_key: self.get_summary_stats(metric_name, self._parse_label_key(label_key))
                for label_key in label_dict.keys()
            }
        
        return result
    
    def get_metric_history(self, metric_name: Optional[str] = None,
                          since: Optional[float] = None,
                          limit: Optional[int] = None) -> List[MetricValue]:
        """Get metric history."""
        with self.history_lock:
            history = self.metric_history.copy()
        
        # Filter by metric name
        if metric_name:
            history = [m for m in history if m.name == metric_name]
        
        # Filter by timestamp
        if since:
            history = [m for m in history if m.timestamp >= since]
        
        # Limit results
        if limit:
            history = history[-limit:]
        
        return history
    
    def add_aggregation_callback(self, callback: Callable[[List[MetricValue]], None]) -> None:
        """Add callback for metric aggregation."""
        self.aggregation_callbacks.append(callback)
    
    def reset_metrics(self) -> None:
        """Reset all metrics."""
        self.counters.clear()
        self.gauges.clear()
        self.histograms.clear()
        self.timers.clear()
        self.summaries.clear()
        
        with self.history_lock:
            self.metric_history.clear()
    
    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format."""
        if format.lower() == "json":
            return json.dumps(self.get_all_metrics(), indent=2)
        elif format.lower() == "prometheus":
            return self._export_prometheus()
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []
        
        # Export counters
        for metric_name, label_dict in self.counters.items():
            for label_key, value in label_dict.items():
                labels = self._parse_label_key(label_key)
                label_str = ","".join([f'{k}="{v}"' for k, v in labels.items()])
                if label_str:
                    label_str = "{" + label_str + "}"
                lines.append(f"{metric_name}{label_str} {value}")
        
        # Export gauges
        for metric_name, label_dict in self.gauges.items():
            for label_key, value in label_dict.items():
                labels = self._parse_label_key(label_key)
                label_str = ","".join([f'{k}="{v}"' for k, v in labels.items()])
                if label_str:
                    label_str = "{" + label_str + "}"
                lines.append(f"{metric_name}{label_str} {value}")
        
        return "\n".join(lines)
    
    def _make_label_key(self, labels: Dict[str, str]) -> str:
        """Create a key from labels dictionary."""
        if not labels:
            return ""
        return ",".join([f"{k}={v}" for k, v in sorted(labels.items())])
    
    def _parse_label_key(self, label_key: str) -> Dict[str, str]:
        """Parse label key back to dictionary."""
        if not label_key:
            return {}
        return dict(pair.split("=", 1) for pair in label_key.split(","))
    
    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile of values."""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile)
        return sorted_values[min(index, len(sorted_values) - 1)]


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def init_metrics_collector(service_name: str, max_history: int = 10000) -> MetricsCollector:
    """Initialize the global metrics collector."""
    global _metrics_collector
    _metrics_collector = MetricsCollector(service_name=service_name, max_history=max_history)
    return _metrics_collector


# Convenience functions
def collect(metric_name: str, value: Union[int, float], 
           metric_type: MetricType = MetricType.GAUGE,
           labels: Optional[Dict[str, str]] = None) -> MetricValue:
    """Collect metric using global collector."""
    return get_metrics_collector().collect(metric_name, value, metric_type, labels)


def increment_counter(metric_name: str, value: int = 1, 
                     labels: Optional[Dict[str, str]] = None) -> MetricValue:
    """Increment counter using global collector."""
    return get_metrics_collector().increment_counter(metric_name, value, labels)


def set_gauge(metric_name: str, value: float, 
              labels: Optional[Dict[str, str]] = None) -> MetricValue:
    """Set gauge using global collector."""
    return get_metrics_collector().set_gauge(metric_name, value, labels)


def time_function(metric_name: str, labels: Optional[Dict[str, str]] = None):
    """Decorator for timing functions using global collector."""
    return get_metrics_collector().time_function(metric_name, labels)


__all__ = [
    "MetricsCollector",
    "MetricValue",
    "MetricType",
    "get_metrics_collector",
    "init_metrics_collector",
    "collect",
    "increment_counter",
    "set_gauge",
    "time_function",
]
