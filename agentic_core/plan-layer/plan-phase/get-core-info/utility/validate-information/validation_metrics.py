"""
L1 Cognitive Planning - Validation Metrics and Telemetry

Provides metrics collection and telemetry hooks for monitoring
validation system performance and health in production environments.
"""

from __future__ import annotations
import logging
import asyncio
import time
from typing import Any, Dict, List, Optional, Union, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from enum import Enum
import json

from pydantic import BaseModel, Field


# ============================================================================
# METRICS TYPES AND INTERFACES
# ============================================================================

class MetricType(str, Enum):
    """Supported metric types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class MetricValue:
    """Individual metric value"""
    name: str
    metric_type: MetricType
    value: Union[int, float]
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ValidationMetrics:
    """Comprehensive validation metrics"""
    validation_type: str
    execution_time_ms: float
    success: bool
    error_count: int
    warning_count: int
    score: float
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class OrchestratorMetrics:
    """Orchestrator-level metrics"""
    total_validations: int
    successful_validations: int
    failed_validations: int
    total_execution_time_ms: float
    average_execution_time_ms: float
    concurrent_validations: int
    timeout_count: int
    fallback_count: int
    timestamp: datetime = field(default_factory=datetime.now)


class MetricsCollectorInterface(ABC):
    """Abstract interface for metrics collection"""
    
    @abstractmethod
    async def collect_metric(self, metric: MetricValue) -> bool:
        """Collect a single metric"""
        pass
    
    @abstractmethod
    async def collect_validation_metrics(self, metrics: ValidationMetrics) -> bool:
        """Collect validation-specific metrics"""
        pass
    
    @abstractmethod
    async def collect_orchestrator_metrics(self, metrics: OrchestratorMetrics) -> bool:
        """Collect orchestrator-specific metrics"""
        pass
    
    @abstractmethod
    async def get_metrics_summary(self, time_window: Optional[timedelta] = None) -> Dict[str, Any]:
        """Get metrics summary for a time window"""
        pass


# ============================================================================
# METRICS COLLECTOR IMPLEMENTATION
# ============================================================================

class InMemoryMetricsCollector(MetricsCollectorInterface):
    """In-memory metrics collector for development and testing"""
    
    def __init__(self, max_metrics: int = 10000):
        self.max_metrics = max_metrics
        self.metrics: List[MetricValue] = []
        self.validation_metrics: List[ValidationMetrics] = []
        self.orchestrator_metrics: List[OrchestratorMetrics] = []
        self.logger = logging.getLogger(__name__)
    
    async def collect_metric(self, metric: MetricValue) -> bool:
        """Collect a single metric"""
        try:
            self.metrics.append(metric)
            
            # Maintain size limit
            if len(self.metrics) > self.max_metrics:
                self.metrics = self.metrics[-self.max_metrics:]
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to collect metric {metric.name}: {str(e)}")
            return False
    
    async def collect_validation_metrics(self, metrics: ValidationMetrics) -> bool:
        """Collect validation-specific metrics"""
        try:
            self.validation_metrics.append(metrics)
            
            # Maintain size limit
            if len(self.validation_metrics) > self.max_metrics:
                self.validation_metrics = self.validation_metrics[-self.max_metrics:]
            
            # Also collect as individual metrics
            await self.collect_metric(MetricValue(
                name="validation_execution_time",
                metric_type=MetricType.HISTOGRAM,
                value=metrics.execution_time_ms,
                labels={"validation_type": metrics.validation_type}
            ))
            
            await self.collect_metric(MetricValue(
                name="validation_success",
                metric_type=MetricType.COUNTER,
                value=1 if metrics.success else 0,
                labels={"validation_type": metrics.validation_type}
            ))
            
            await self.collect_metric(MetricValue(
                name="validation_score",
                metric_type=MetricType.GAUGE,
                value=metrics.score,
                labels={"validation_type": metrics.validation_type}
            ))
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to collect validation metrics: {str(e)}")
            return False
    
    async def collect_orchestrator_metrics(self, metrics: OrchestratorMetrics) -> bool:
        """Collect orchestrator-specific metrics"""
        try:
            self.orchestrator_metrics.append(metrics)
            
            # Maintain size limit
            if len(self.orchestrator_metrics) > self.max_metrics:
                self.orchestrator_metrics = self.orchestrator_metrics[-self.max_metrics:]
            
            # Also collect as individual metrics
            await self.collect_metric(MetricValue(
                name="orchestrator_total_validations",
                metric_type=MetricType.COUNTER,
                value=metrics.total_validations
            ))
            
            await self.collect_metric(MetricValue(
                name="orchestrator_success_rate",
                metric_type=MetricType.GAUGE,
                value=(metrics.successful_validations / metrics.total_validations * 100) if metrics.total_validations > 0 else 0
            ))
            
            await self.collect_metric(MetricValue(
                name="orchestrator_average_execution_time",
                metric_type=MetricType.GAUGE,
                value=metrics.average_execution_time_ms
            ))
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to collect orchestrator metrics: {str(e)}")
            return False
    
    async def get_metrics_summary(self, time_window: Optional[timedelta] = None) -> Dict[str, Any]:
        """Get metrics summary for a time window"""
        try:
            cutoff_time = datetime.now() - time_window if time_window else datetime.min
            
            # Filter metrics by time window
            recent_metrics = [m for m in self.metrics if m.timestamp >= cutoff_time]
            recent_validation_metrics = [m for m in self.validation_metrics if m.timestamp >= cutoff_time]
            recent_orchestrator_metrics = [m for m in self.orchestrator_metrics if m.timestamp >= cutoff_time]
            
            # Calculate summaries
            validation_summary = {}
            for validation_type in set(m.validation_type for m in recent_validation_metrics):
                type_metrics = [m for m in recent_validation_metrics if m.validation_type == validation_type]
                validation_summary[validation_type] = {
                    "count": len(type_metrics),
                    "success_rate": sum(1 for m in type_metrics if m.success) / len(type_metrics) * 100 if type_metrics else 0,
                    "average_execution_time": sum(m.execution_time_ms for m in type_metrics) / len(type_metrics) if type_metrics else 0,
                    "average_score": sum(m.score for m in type_metrics) / len(type_metrics) if type_metrics else 0,
                    "total_errors": sum(m.error_count for m in type_metrics),
                    "total_warnings": sum(m.warning_count for m in type_metrics)
                }
            
            orchestrator_summary = {}
            if recent_orchestrator_metrics:
                latest = recent_orchestrator_metrics[-1]
                orchestrator_summary = {
                    "total_validations": latest.total_validations,
                    "success_rate": (latest.successful_validations / latest.total_validations * 100) if latest.total_validations > 0 else 0,
                    "average_execution_time": latest.average_execution_time_ms,
                    "timeout_count": latest.timeout_count,
                    "fallback_count": latest.fallback_count
                }
            
            return {
                "time_window": str(time_window) if time_window else "all",
                "metrics_collected": len(recent_metrics),
                "validation_summary": validation_summary,
                "orchestrator_summary": orchestrator_summary,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate metrics summary: {str(e)}")
            return {}


class PrometheusMetricsCollector(MetricsCollectorInterface):
    """Prometheus-compatible metrics collector for production monitoring"""
    
    def __init__(self, prefix: str = "validation_system"):
        self.prefix = prefix
        self.metrics: Dict[str, MetricValue] = {}
        self.logger = logging.getLogger(__name__)
    
    async def collect_metric(self, metric: MetricValue) -> bool:
        """Collect a single metric in Prometheus format"""
        try:
            metric_key = f"{self.prefix}_{metric.name}"
            self.metrics[metric_key] = metric
            return True
        except Exception as e:
            self.logger.error(f"Failed to collect Prometheus metric {metric.name}: {str(e)}")
            return False
    
    async def collect_validation_metrics(self, metrics: ValidationMetrics) -> bool:
        """Collect validation-specific metrics in Prometheus format"""
        try:
            await self.collect_metric(MetricValue(
                name="validation_execution_time_ms",
                metric_type=MetricType.HISTOGRAM,
                value=metrics.execution_time_ms,
                labels={"validation_type": metrics.validation_type}
            ))
            
            await self.collect_metric(MetricValue(
                name="validation_success_total",
                metric_type=MetricType.COUNTER,
                value=1 if metrics.success else 0,
                labels={"validation_type": metrics.validation_type}
            ))
            
            await self.collect_metric(MetricValue(
                name="validation_score",
                metric_type=MetricType.GAUGE,
                value=metrics.score,
                labels={"validation_type": metrics.validation_type}
            ))
            
            await self.collect_metric(MetricValue(
                name="validation_errors_total",
                metric_type=MetricType.COUNTER,
                value=metrics.error_count,
                labels={"validation_type": metrics.validation_type}
            ))
            
            await self.collect_metric(MetricValue(
                name="validation_warnings_total",
                metric_type=MetricType.COUNTER,
                value=metrics.warning_count,
                labels={"validation_type": metrics.validation_type}
            ))
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to collect validation Prometheus metrics: {str(e)}")
            return False
    
    async def collect_orchestrator_metrics(self, metrics: OrchestratorMetrics) -> bool:
        """Collect orchestrator-specific metrics in Prometheus format"""
        try:
            await self.collect_metric(MetricValue(
                name="orchestrator_validations_total",
                metric_type=MetricType.COUNTER,
                value=metrics.total_validations
            ))
            
            await self.collect_metric(MetricValue(
                name="orchestrator_successful_validations_total",
                metric_type=MetricType.COUNTER,
                value=metrics.successful_validations
            ))
            
            await self.collect_metric(MetricValue(
                name="orchestrator_failed_validations_total",
                metric_type=MetricType.COUNTER,
                value=metrics.failed_validations
            ))
            
            await self.collect_metric(MetricValue(
                name="orchestrator_execution_time_ms",
                metric_type=MetricType.GAUGE,
                value=metrics.average_execution_time_ms
            ))
            
            await self.collect_metric(MetricValue(
                name="orchestrator_concurrent_validations",
                metric_type=MetricType.GAUGE,
                value=metrics.concurrent_validations
            ))
            
            await self.collect_metric(MetricValue(
                name="orchestrator_timeouts_total",
                metric_type=MetricType.COUNTER,
                value=metrics.timeout_count
            ))
            
            await self.collect_metric(MetricValue(
                name="orchestrator_fallbacks_total",
                metric_type=MetricType.COUNTER,
                value=metrics.fallback_count
            ))
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to collect orchestrator Prometheus metrics: {str(e)}")
            return False
    
    async def get_metrics_summary(self, time_window: Optional[timedelta] = None) -> Dict[str, Any]:
        """Get metrics summary in Prometheus format"""
        try:
            prometheus_metrics = []
            
            for metric_key, metric in self.metrics.items():
                label_str = ""
                if metric.labels:
                    label_pairs = [f'{k}="{v}"' for k, v in metric.labels.items()]
                    label_str = "{" + ",".join(label_pairs) + "}"
                
                prometheus_metrics.append(f"{metric_key}{label_str} {metric.value}")
            
            return {
                "format": "prometheus",
                "metrics": prometheus_metrics,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate Prometheus metrics summary: {str(e)}")
            return {}


# ============================================================================
# METRICS DECORATORS AND UTILITIES
# ============================================================================

def collect_validation_metrics(validation_type: str, metrics_collector: MetricsCollectorInterface):
    """Decorator to automatically collect validation metrics"""
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            success = False
            error_count = 0
            warning_count = 0
            score = 0.0
            
            try:
                result = await func(*args, **kwargs)
                
                # Extract metrics from result
                if hasattr(result, 'validation_result'):
                    validation_result = result.validation_result
                    success = getattr(validation_result, 'is_valid', False) or getattr(validation_result, 'is_secure', False) or getattr(validation_result, 'is_performant', False) or getattr(validation_result, 'is_reliable', False) or getattr(validation_result, 'is_scalable', False) or getattr(validation_result, 'is_maintainable', False) or getattr(validation_result, 'is_complete', False)
                    error_count = len(getattr(validation_result, 'validation_errors', []))
                    warning_count = len(getattr(validation_result, 'validation_warnings', []))
                    score = getattr(validation_result, 'security_score', getattr(validation_result, 'performance_score', getattr(validation_result, 'reliability_score', getattr(validation_result, 'scalability_score', getattr(validation_result, 'maintainability_score', getattr(validation_result, 'completeness_score', 0.0))))))
                
                return result
                
            except Exception as e:
                success = False
                error_count = 1
                raise
            finally:
                execution_time_ms = (time.time() - start_time) * 1000
                
                # Collect metrics
                validation_metrics = ValidationMetrics(
                    validation_type=validation_type,
                    execution_time_ms=execution_time_ms,
                    success=success,
                    error_count=error_count,
                    warning_count=warning_count,
                    score=score
                )
                
                await metrics_collector.collect_validation_metrics(validation_metrics)
        
        return wrapper
    return decorator


def collect_orchestrator_metrics(metrics_collector: MetricsCollectorInterface):
    """Decorator to automatically collect orchestrator metrics"""
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                # Extract metrics from result
                total_validations = len(result.validation_results) if hasattr(result, 'validation_results') else 0
                successful_validations = sum(1 for r in result.validation_results if r.is_valid) if hasattr(result, 'validation_results') else 0
                failed_validations = total_validations - successful_validations
                total_execution_time_ms = (time.time() - start_time) * 1000
                average_execution_time_ms = total_execution_time_ms / total_validations if total_validations > 0 else 0
                
                orchestrator_metrics = OrchestratorMetrics(
                    total_validations=total_validations,
                    successful_validations=successful_validations,
                    failed_validations=failed_validations,
                    total_execution_time_ms=total_execution_time_ms,
                    average_execution_time_ms=average_execution_time_ms,
                    concurrent_validations=total_validations,
                    timeout_count=0,  # Would be set by timeout handling
                    fallback_count=1 if "fallback_mode" in result.flags else 0
                )
                
                await metrics_collector.collect_orchestrator_metrics(orchestrator_metrics)
                
                return result
                
            except Exception as e:
                # Collect failure metrics
                orchestrator_metrics = OrchestratorMetrics(
                    total_validations=0,
                    successful_validations=0,
                    failed_validations=1,
                    total_execution_time_ms=(time.time() - start_time) * 1000,
                    average_execution_time_ms=0,
                    concurrent_validations=0,
                    timeout_count=0,
                    fallback_count=0
                )
                
                await metrics_collector.collect_orchestrator_metrics(orchestrator_metrics)
                raise
        
        return wrapper
    return decorator


# ============================================================================
# METRICS HEALTH MONITORING
# ============================================================================

@dataclass
class HealthStatus:
    """Health status of the validation system"""
    healthy: bool
    status_message: str
    metrics_collector_healthy: bool
    recent_success_rate: float
    recent_average_execution_time: float
    error_rate: float
    timestamp: datetime = field(default_factory=datetime.now)


class MetricsHealthMonitor:
    """Health monitoring for the validation system"""
    
    def __init__(self, metrics_collector: MetricsCollectorInterface):
        self.metrics_collector = metrics_collector
        self.logger = logging.getLogger(__name__)
    
    async def get_health_status(self, time_window: timedelta = timedelta(minutes=5)) -> HealthStatus:
        """Get current health status"""
        try:
            # Get recent metrics
            summary = await self.metrics_collector.get_metrics_summary(time_window)
            
            # Check metrics collector health
            metrics_healthy = len(summary.get("metrics_collected", 0)) > 0
            
            # Calculate health indicators
            validation_summary = summary.get("validation_summary", {})
            orchestrator_summary = summary.get("orchestrator_summary", {})
            
            recent_success_rate = orchestrator_summary.get("success_rate", 100.0)
            recent_average_execution_time = orchestrator_summary.get("average_execution_time", 0.0)
            
            # Calculate error rate
            total_errors = sum(v.get("total_errors", 0) for v in validation_summary.values())
            total_validations = sum(v.get("count", 0) for v in validation_summary.values())
            error_rate = (total_errors / total_validations * 100) if total_validations > 0 else 0.0
            
            # Determine overall health
            healthy = (
                metrics_healthy and
                recent_success_rate >= 90.0 and
                recent_average_execution_time <= 10000 and  # 10 seconds
                error_rate <= 10.0
            )
            
            status_message = "Healthy" if healthy else "Unhealthy"
            if not metrics_healthy:
                status_message = "Metrics collector unhealthy"
            elif recent_success_rate < 90.0:
                status_message = f"Low success rate: {recent_success_rate:.1f}%"
            elif recent_average_execution_time > 10000:
                status_message = f"High execution time: {recent_average_execution_time:.1f}ms"
            elif error_rate > 10.0:
                status_message = f"High error rate: {error_rate:.1f}%"
            
            return HealthStatus(
                healthy=healthy,
                status_message=status_message,
                metrics_collector_healthy=metrics_healthy,
                recent_success_rate=recent_success_rate,
                recent_average_execution_time=recent_average_execution_time,
                error_rate=error_rate
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get health status: {str(e)}")
            return HealthStatus(
                healthy=False,
                status_message=f"Health check failed: {str(e)}",
                metrics_collector_healthy=False,
                recent_success_rate=0.0,
                recent_average_execution_time=0.0,
                error_rate=100.0
            )


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_in_memory_metrics_collector(max_metrics: int = 10000) -> InMemoryMetricsCollector:
    """Create in-memory metrics collector"""
    return InMemoryMetricsCollector(max_metrics)


def create_prometheus_metrics_collector(prefix: str = "validation_system") -> PrometheusMetricsCollector:
    """Create Prometheus metrics collector"""
    return PrometheusMetricsCollector(prefix)


def create_metrics_health_monitor(metrics_collector: MetricsCollectorInterface) -> MetricsHealthMonitor:
    """Create metrics health monitor"""
    return MetricsHealthMonitor(metrics_collector)


# ============================================================================
# GLOBAL METRICS INSTANCE
# ============================================================================

_global_metrics_collector: Optional[MetricsCollectorInterface] = None
_global_health_monitor: Optional[MetricsHealthMonitor] = None


def get_global_metrics_collector() -> MetricsCollectorInterface:
    """Get global metrics collector instance"""
    global _global_metrics_collector
    if _global_metrics_collector is None:
        _global_metrics_collector = create_in_memory_metrics_collector()
    return _global_metrics_collector


def set_global_metrics_collector(collector: MetricsCollectorInterface):
    """Set global metrics collector instance"""
    global _global_metrics_collector
    _global_metrics_collector = collector


def get_global_health_monitor() -> MetricsHealthMonitor:
    """Get global health monitor instance"""
    global _global_health_monitor
    if _global_health_monitor is None:
        _global_health_monitor = create_metrics_health_monitor(get_global_metrics_collector())
    return _global_health_monitor


def set_global_health_monitor(monitor: MetricsHealthMonitor):
    """Set global health monitor instance"""
    global _global_health_monitor
    _global_health_monitor = monitor
