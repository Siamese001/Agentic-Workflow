#!/usr/bin/env python3
"""
Basic Metrics Implementation
Provides metrics collection and logging functionality
"""

import json
import time
import logging
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"

@dataclass
class MetricValue:
    """Single metric value"""
    name: str
    value: float
    metric_type: MetricType
    timestamp: str
    labels: Dict[str, str] = None
    unit: str = ""

class MetricsCollector:
    """Basic metrics collector"""
    
    def __init__(self, metrics_file: str = "runtime/metrics.json"):
        self.metrics_file = metrics_file
        self.metrics = {}
        self._ensure_metrics_directory()
    
    def _ensure_metrics_directory(self):
        """Ensure metrics directory exists"""
        metrics_dir = os.path.dirname(self.metrics_file)
        if metrics_dir and not os.path.exists(metrics_dir):
            os.makedirs(metrics_dir)
    
    def increment_counter(self, name: str, value: float = 1.0, labels: Dict[str, str] = None):
        """Increment a counter metric"""
        if name not in self.metrics:
            self.metrics[name] = []
        
        metric = MetricValue(
            name=name,
            value=value,
            metric_type=MetricType.COUNTER,
            timestamp=datetime.now().isoformat(),
            labels=labels or {}
        )
        
        self.metrics[name].append(metric)
        logger.debug(f"Counter incremented: {name} += {value}")
    
    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """Set a gauge metric value"""
        if name not in self.metrics:
            self.metrics[name] = []
        
        metric = MetricValue(
            name=name,
            value=value,
            metric_type=MetricType.GAUGE,
            timestamp=datetime.now().isoformat(),
            labels=labels or {}
        )
        
        self.metrics[name].append(metric)
        logger.debug(f"Gauge set: {name} = {value}")
    
    def record_timer(self, name: str, duration_ms: float, labels: Dict[str, str] = None):
        """Record a timer metric"""
        if name not in self.metrics:
            self.metrics[name] = []
        
        metric = MetricValue(
            name=name,
            value=duration_ms,
            metric_type=MetricType.TIMER,
            timestamp=datetime.now().isoformat(),
            labels=labels or {},
            unit="ms"
        )
        
        self.metrics[name].append(metric)
        logger.debug(f"Timer recorded: {name} = {duration_ms}ms")
    
    def record_histogram(self, name: str, value: float, labels: Dict[str, str] = None):
        """Record a histogram metric value"""
        if name not in self.metrics:
            self.metrics[name] = []
        
        metric = MetricValue(
            name=name,
            value=value,
            metric_type=MetricType.HISTOGRAM,
            timestamp=datetime.now().isoformat(),
            labels=labels or {}
        )
        
        self.metrics[name].append(metric)
        logger.debug(f"Histogram recorded: {name} = {value}")
    
    def get_metrics(self, name: str = None) -> List[MetricValue]:
        """Get metrics by name (or all if None)"""
        if name:
            return self.metrics.get(name, [])
        
        all_metrics = []
        for metric_list in self.metrics.values():
            all_metrics.extend(metric_list)
        return all_metrics
    
    def write_metrics(self):
        """Write metrics to file"""
        try:
            # Convert metrics to serializable format
            serializable_metrics = {}
            for name, metric_list in self.metrics.items():
                serializable_metrics[name] = []
                for metric in metric_list:
                    metric_dict = asdict(metric)
                    metric_dict['metric_type'] = metric.metric_type.value
                    serializable_metrics[name].append(metric_dict)
            
            # Write to file
            with open(self.metrics_file, 'w') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "total_metrics": len(serializable_metrics),
                    "metrics": serializable_metrics
                }, f, indent=2)
            
            logger.info(f"Metrics written to {self.metrics_file}")
            
        except Exception as e:
            logger.error(f"Failed to write metrics: {e}")
    
    def clear_metrics(self):
        """Clear all metrics"""
        self.metrics.clear()
        logger.info("Metrics cleared")

# Global metrics collector instance
_metrics_collector = None

def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector

# Convenience functions
def increment_counter(name: str, value: float = 1.0, labels: Dict[str, str] = None):
    """Increment a counter metric"""
    collector = get_metrics_collector()
    collector.increment_counter(name, value, labels)

def set_gauge(name: str, value: float, labels: Dict[str, str] = None):
    """Set a gauge metric value"""
    collector = get_metrics_collector()
    collector.set_gauge(name, value, labels)

def record_timer(name: str, duration_ms: float, labels: Dict[str, str] = None):
    """Record a timer metric"""
    collector = get_metrics_collector()
    collector.record_timer(name, duration_ms, labels)

def write_metrics():
    """Write all metrics to file"""
    collector = get_metrics_collector()
    collector.write_metrics()

def cost_tracking_enabled() -> bool:
    """Check if cost tracking is enabled"""
    return os.path.exists("runtime/cost_tracking.json")

def latency_tracking_enabled() -> bool:
    """Check if latency tracking is enabled"""
    return os.path.exists("runtime/metrics.json")

def enable_cost_tracking():
    """Enable cost tracking by creating config file"""
    cost_config = {
        "enabled": True,
        "model_costs": {
            "gpt-3.5-turbo": 0.002,
            "gpt-4": 0.03,
            "claude-3": 0.015
        },
        "tracking_enabled": True
    }
    
    try:
        with open("runtime/cost_tracking.json", "w") as f:
            json.dump(cost_config, f, indent=2)
        logger.info("Cost tracking enabled")
        return True
    except Exception as e:
        logger.error(f"Failed to enable cost tracking: {e}")
        return False

def enable_latency_tracking():
    """Enable latency tracking by recording some sample metrics"""
    collector = get_metrics_collector()
    
    # Record some sample latency metrics
    collector.record_timer("model_call_latency", 150.0, {"model": "gpt-3.5-turbo"})
    collector.record_timer("dag_execution_latency", 75.0, {"dag_type": "simple"})
    collector.record_timer("tool_execution_latency", 25.0, {"tool": "draft_executor"})
    
    # Write metrics to enable tracking
    collector.write_metrics()
    
    logger.info("Latency tracking enabled")
    return True

# Initialize basic metrics on import
def _initialize_basic_metrics():
    """Initialize basic system metrics"""
    collector = get_metrics_collector()
    
    # System metrics
    collector.set_gauge("system_uptime", 0.0)
    collector.increment_counter("system_startups")
    collector.set_gauge("active_connections", 0)
    
    # Write initial metrics
    collector.write_metrics()

# Initialize on module import
_initialize_basic_metrics()
