"""
L1 Cognitive Planning - Prepare Information Metrics and Telemetry

Provides metrics collection and telemetry hooks for monitoring
prepare information system performance and health in production environments.
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

class PrepareMetricType(str, Enum):
    """Supported metric types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class PrepareMetricValue:
    """Individual metric value"""
    name: str
    metric_type: PrepareMetricType
    value: Union[int, float]
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PrepareInformationMetrics:
    """Comprehensive prepare information metrics"""
    preparation_type: str
    execution_time_ms: float
    success: bool
    error_count: int
    warning_count: int
    score: float
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PrepareOrchestratorMetrics:
    """Prepare orchestrator-level metrics"""
    total_preparations: int
    successful_preparations: int
    failed_preparations: int
    total_execution_time_ms: float
    average_execution_time_ms: float
    concurrent_preparations: int
    timeout_count: int
    fallback_count: int
    timestamp: datetime = field(default_factory=datetime.now)


class PrepareMetricsCollectorInterface(ABC):
    """Abstract interface for prepare information metrics collection"""
    
    @abstractmethod
    async def collect_metric(self, metric: PrepareMetricValue) -> bool:
        """Collect a single metric"""
        pass
    
    @abstractmethod
    async def collect_prepare_metrics(self, metrics: PrepareInformationMetrics) -> bool:
        """Collect preparation-specific metrics"""
        pass
    
    @abstractmethod
    async def collect_prepare_orchestrator_metrics(self, metrics: PrepareOrchestratorMetrics) -> bool:
        """Collect orchestrator-specific metrics"""
        pass
    
    @abstractmethod
    async def get_metrics_summary(self, time_window: Optional[timedelta] = None) -> Dict[str, Any]:
        """Get metrics summary for a time window"""
        pass


# ============================================================================
# METRICS COLLECTOR IMPLEMENTATION
# ============================================================================

class PrepareInMemoryMetricsCollector(PrepareMetricsCollectorInterface):
    """In-memory metrics collector for development and testing"""
    
    def __init__(self, max_metrics: int = 5000):
        self.max_metrics = max_metrics
        self.metrics: List[PrepareMetricValue] = []
        self.prepare_metrics: List[PrepareInformationMetrics] = []
        self.orchestrator_metrics: List[PrepareOrchestratorMetrics] = []
        self.logger = logging.getLogger(__name__)
    
    async def collect_metric(self, metric: PrepareMetricValue) -> bool:
        """Collect a single metric"""
        try:
            self.metrics.append(metric)
            
            # Maintain size limit
            if len(self.metrics) > self.max_metrics:
                self.metrics = self.metrics[-self.max_metrics:]
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to collect prepare metric {metric.name}: {str(e)}")
            return False
    
    async def collect_prepare_metrics(self, metrics: PrepareInformationMetrics) -> bool:
        """Collect preparation-specific metrics"""
        try:
            self.prepare_metrics.append(metrics)
            
            # Maintain size limit
            if len(self.prepare_metrics) > self.max_metrics:
                self.prepare_metrics = self.prepare_metrics[-self.max_metrics:]
            
            # Also collect as individual metrics
            await self.collect_metric(PrepareMetricValue(
                name="prepare_execution_time",
                metric_type=PrepareMetricType.HISTOGRAM,
                value=metrics.execution_time_ms,
                labels={"preparation_type": metrics.preparation_type}
            ))
            
            await self.collect_metric(PrepareMetricValue(
                name="prepare_success",
                metric_type=PrepareMetricType.COUNTER,
                value=1 if metrics.success else 0,
                labels={"preparation_type": metrics.preparation_type}
            ))
            
            await self.collect_metric(PrepareMetricValue(
                name="prepare_score",
                metric_type=PrepareMetricType.GAUGE,
                value=metrics.score,
                labels={"preparation_type": metrics.preparation_type}
            ))
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to collect prepare metrics: {str(e)}")
            return False
    
    async def collect_prepare_orchestrator_metrics(self, metrics: PrepareOrchestratorMetrics) -> bool:
        """Collect orchestrator-specific metrics"""
        try:
            self.orchestrator_metrics.append(metrics)
            
            # Maintain size limit
            if len(self.orchestrator_metrics) > self.max_metrics:
                self.orchestrator_metrics = self.orchestrator_metrics[-self.max_metrics:]
            
            # Also collect as individual metrics
            await self.collect_metric(PrepareMetricValue(
                name="prepare_orchestrator_total_preparations",
                metric_type=PrepareMetricType.COUNTER,
                value=metrics.total_preparations
            ))
            
            await self.collect_metric(PrepareMetricValue(
                name="prepare_orchestrator_success_rate",
                metric_type=PrepareMetricType.GAUGE,
                value=(metrics.successful_preparations / metrics.total_preparations * 100) if metrics.total_preparations > 0 else 0
            ))
            
            await self.collect_metric(PrepareMetricValue(
                name="prepare_orchestrator_average_execution_time",
                metric_type=PrepareMetricType.GAUGE,
                value=metrics.average_execution_time_ms
            ))
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to collect prepare orchestrator metrics: {str(e)}")
            return False
    
    async def get_metrics_summary(self, time_window: Optional[timedelta] = None) -> Dict[str, Any]:
        """Get metrics summary for a time window"""
        try:
            cutoff_time = datetime.now() - time_window if time_window else datetime.min
            
            # Filter metrics by time window
            recent_metrics = [m for m in self.metrics if m.timestamp >= cutoff_time]
            recent_prepare_metrics = [m for m in self.prepare_metrics if m.timestamp >= cutoff_time]
            recent_orchestrator_metrics = [m for m in self.orchestrator_metrics if m.timestamp >= cutoff_time]
            
            # Calculate summaries
            preparation_summary = {}
            for preparation_type in set(m.preparation_type for m in recent_prepare_metrics):
                type_metrics = [m for m in recent_prepare_metrics if m.preparation_type == preparation_type]
                preparation_summary[preparation_type] = {
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
                    "total_preparations": latest.total_preparations,
                    "success_rate": (latest.successful_preparations / latest.total_preparations * 100) if latest.total_preparations > 0 else 0,
                    "average_execution_time": latest.average_execution_time_ms,
                    "timeout_count": latest.timeout_count,
                    "fallback_count": latest.fallback_count
                }
            
            return {
                "time_window": str(time_window) if time_window else "all",
                "metrics_collected": len(recent_metrics),
                "preparation_summary": preparation_summary,
                "orchestrator_summary": orchestrator_summary,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate prepare metrics summary: {str(e)}")
            return {}


class PreparePrometheusMetricsCollector(PrepareMetricsCollectorInterface):
    """Prometheus-compatible metrics collector for production monitoring"""
    
    def __init__(self, prefix: str = "prepare_information_system"):
        self.prefix = prefix
        self.metrics: Dict[str, PrepareMetricValue] = {}
        self.logger = logging.getLogger(__name__)
    
    async def collect_metric(self, metric: PrepareMetricValue) -> bool:
        """Collect a single metric in Prometheus format"""
        try:
            metric_key = f"{self.prefix}_{metric.name}"
            self.metrics[metric_key] = metric
            return True
        except Exception as e:
            self.logger.error(f"Failed to collect Prometheus prepare metric {metric.name}: {str(e)}")
            return False
    
    async def collect_prepare_metrics(self, metrics: PrepareInformationMetrics) -> bool:
        """Collect preparation-specific metrics in Prometheus format"""
        try:
            await self.collect_metric(PrepareMetricValue(
                name="preparation_execution_time_ms",
                metric_type=PrepareMetricType.HISTOGRAM,
                value=metrics.execution_time_ms,
                labels={"preparation_type": metrics.preparation_type}
            ))
            
            await self.collect_metric(PrepareMetricValue(
                name="preparation_success_total",
                metric_type=PrepareMetricType.COUNTER,
                value=1 if metrics.success else 0,
                labels={"preparation_type": metrics.preparation_type}
            ))
            
            await self.collect_metric(PrepareMetricValue(
                name="preparation_score",
                metric_type=PrepareMetricType.GAUGE,
                value=metrics.score,
                labels={"preparation_type": metrics.preparation_type}
            ))
            
            await self.collect_metric(PrepareMetricValue(
                name="preparation_errors_total",
                metric_type=PrepareMetricType.COUNTER,
                value=metrics.error_count,
                labels={"preparation_type": metrics.preparation_type}
            ))
            
            await self.collect_metric(PrepareMetricValue(
                name="preparation_warnings_total",
                metric_type=PrepareMetricType.COUNTER,
                value=metrics.warning_count,
                labels={"preparation_type": metrics.preparation_type}
            ))
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to collect preparation Prometheus metrics: {str(e)}")
            return False
    
    async def collect_prepare_orchestrator_metrics(self, metrics: PrepareOrchestratorMetrics) -> bool:
        """Collect orchestrator-specific metrics in Prometheus format"""
        try:
            await self.collect_metric(PrepareMetricValue(
                name="prepare_orchestrator_preparations_total",
                metric_type=PrepareMetricType.COUNTER,
                value=metrics.total_preparations
            ))
            
            await self.collect_metric(PrepareMetricValue(
                name="prepare_orchestrator_successful_preparations_total",
                metric_type=PrepareMetricType.COUNTER,
                value=metrics.successful_preparations
            ))
            
            await self.collect_metric(PrepareMetricValue(
                name="prepare_orchestrator_failed_preparations_total",
                metric_type=PrepareMetricType.COUNTER,
                value=metrics.failed_preparations
            ))
            
            await self.collect_metric(PrepareMetricValue(
                name="prepare_orchestrator_execution_time_ms",
                metric_type=PrepareMetricType.GAUGE,
                value=metrics.average_execution_time_ms
            ))
            
            await self.collect_metric(PrepareMetricValue(
                name="prepare_orchestrator_concurrent_preparations",
                metric_type=PrepareMetricType.GAUGE,
                value=metrics.concurrent_preparations
            ))
            
            await self.collect_metric(PrepareMetricValue(
                name="prepare_orchestrator_timeouts_total",
                metric_type=PrepareMetricType.COUNTER,
                value=metrics.timeout_count
            ))
            
            await self.collect_metric(PrepareMetricValue(
                name="prepare_orchestrator_fallbacks_total",
                metric_type=PrepareMetricType.COUNTER,
                value=metrics.fallback_count
            ))
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to collect prepare orchestrator Prometheus metrics: {str(e)}")
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
            self.logger.error(f"Failed to generate Prometheus prepare metrics summary: {str(e)}")
            return {}


# ============================================================================
# METRICS DECORATORS AND UTILITIES
# ============================================================================

def collect_prepare_metrics(preparation_type: str, metrics_collector: PrepareMetricsCollectorInterface):
    """Decorator to automatically collect preparation metrics"""
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
                if hasattr(result, 'is_formatted'):
                    success = result.is_formatted
                    error_count = len(getattr(result, 'formatting_errors', []))
                    warning_count = len(getattr(result, 'formatting_warnings', []))
                    score = getattr(result, 'formatting_score', 0.0)
                elif hasattr(result, 'is_prepared'):
                    success = result.is_prepared
                    error_count = len(getattr(result, 'preparation_errors', []))
                    warning_count = len(getattr(result, 'preparation_warnings', []))
                    score = getattr(result, 'preparation_score', 0.0)
                
                return result
                
            except Exception as e:
                success = False
                error_count = 1
                raise
            finally:
                execution_time_ms = (time.time() - start_time) * 1000
                
                # Collect metrics
                prepare_metrics = PrepareInformationMetrics(
                    preparation_type=preparation_type,
                    execution_time_ms=execution_time_ms,
                    success=success,
                    error_count=error_count,
                    warning_count=warning_count,
                    score=score
                )
                
                await metrics_collector.collect_prepare_metrics(prepare_metrics)
        
        return wrapper
    return decorator


def collect_prepare_orchestrator_metrics(metrics_collector: PrepareMetricsCollectorInterface):
    """Decorator to automatically collect orchestrator metrics"""
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                # Extract metrics from result
                total_preparations = len(result.preparation_results) if hasattr(result, 'preparation_results') else 0
                successful_preparations = sum(1 for r in result.preparation_results if r.is_successful) if hasattr(result, 'preparation_results') else 0
                failed_preparations = total_preparations - successful_preparations
                total_execution_time_ms = (time.time() - start_time) * 1000
                average_execution_time_ms = total_execution_time_ms / total_preparations if total_preparations > 0 else 0
                
                orchestrator_metrics = PrepareOrchestratorMetrics(
                    total_preparations=total_preparations,
                    successful_preparations=successful_preparations,
                    failed_preparations=failed_preparations,
                    total_execution_time_ms=total_execution_time_ms,
                    average_execution_time_ms=average_execution_time_ms,
                    concurrent_preparations=total_preparations,
                    timeout_count=0,  # Would be set by timeout handling
                    fallback_count=1 if "fallback_mode" in result.flags else 0
                )
                
                await metrics_collector.collect_prepare_orchestrator_metrics(orchestrator_metrics)
                
                return result
                
            except Exception as e:
                # Collect failure metrics
                orchestrator_metrics = PrepareOrchestratorMetrics(
                    total_preparations=0,
                    successful_preparations=0,
                    failed_preparations=1,
                    total_execution_time_ms=(time.time() - start_time) * 1000,
                    average_execution_time_ms=0,
                    concurrent_preparations=0,
                    timeout_count=0,
                    fallback_count=0
                )
                
                await metrics_collector.collect_prepare_orchestrator_metrics(orchestrator_metrics)
                raise
        
        return wrapper
    return decorator


# ============================================================================
# METRICS HEALTH MONITORING
# ============================================================================

@dataclass
class PrepareHealthStatus:
    """Health status of the prepare information system"""
    healthy: bool
    status_message: str
    metrics_collector_healthy: bool
    recent_success_rate: float
    recent_average_execution_time: float
    error_rate: float
    timestamp: datetime = field(default_factory=datetime.now)


class PrepareMetricsHealthMonitor:
    """Health monitoring for the prepare information system"""
    
    def __init__(self, metrics_collector: PrepareMetricsCollectorInterface):
        self.metrics_collector = metrics_collector
        self.logger = logging.getLogger(__name__)
    
    async def get_health_status(self, time_window: timedelta = timedelta(minutes=5)) -> PrepareHealthStatus:
        """Get current health status"""
        try:
            # Get recent metrics
            summary = await self.metrics_collector.get_metrics_summary(time_window)
            
            # Check metrics collector health
            metrics_healthy = len(summary.get("metrics_collected", 0)) > 0
            
            # Calculate health indicators
            preparation_summary = summary.get("preparation_summary", {})
            orchestrator_summary = summary.get("orchestrator_summary", {})
            
            recent_success_rate = orchestrator_summary.get("success_rate", 100.0)
            recent_average_execution_time = orchestrator_summary.get("average_execution_time", 0.0)
            
            # Calculate error rate
            total_errors = sum(v.get("total_errors", 0) for v in preparation_summary.values())
            total_preparations = sum(v.get("count", 0) for v in preparation_summary.values())
            error_rate = (total_errors / total_preparations * 100) if total_preparations > 0 else 0.0
            
            # Determine overall health
            healthy = (
                metrics_healthy and
                recent_success_rate >= 90.0 and
                recent_average_execution_time <= 5000 and  # 5 seconds
                error_rate <= 10.0
            )
            
            status_message = "Healthy" if healthy else "Unhealthy"
            if not metrics_healthy:
                status_message = "Prepare metrics collector unhealthy"
            elif recent_success_rate < 90.0:
                status_message = f"Low success rate: {recent_success_rate:.1f}%"
            elif recent_average_execution_time > 5000:
                status_message = f"High execution time: {recent_average_execution_time:.1f}ms"
            elif error_rate > 10.0:
                status_message = f"High error rate: {error_rate:.1f}%"
            
            return PrepareHealthStatus(
                healthy=healthy,
                status_message=status_message,
                metrics_collector_healthy=metrics_healthy,
                recent_success_rate=recent_success_rate,
                recent_average_execution_time=recent_average_execution_time,
                error_rate=error_rate
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get prepare health status: {str(e)}")
            return PrepareHealthStatus(
                healthy=False,
                status_message=f"Prepare health check failed: {str(e)}",
                metrics_collector_healthy=False,
                recent_success_rate=0.0,
                recent_average_execution_time=0.0,
                error_rate=100.0
            )


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_prepare_in_memory_metrics_collector(max_metrics: int = 5000) -> PrepareInMemoryMetricsCollector:
    """Create in-memory prepare metrics collector"""
    return PrepareInMemoryMetricsCollector(max_metrics)


def create_prepare_prometheus_metrics_collector(prefix: str = "prepare_information_system") -> PreparePrometheusMetricsCollector:
    """Create Prometheus prepare metrics collector"""
    return PreparePrometheusMetricsCollector(prefix)


def create_prepare_metrics_health_monitor(metrics_collector: PrepareMetricsCollectorInterface) -> PrepareMetricsHealthMonitor:
    """Create prepare metrics health monitor"""
    return PrepareMetricsHealthMonitor(metrics_collector)


# ============================================================================
# GLOBAL METRICS INSTANCE
# ============================================================================

_global_prepare_metrics_collector: Optional[PrepareMetricsCollectorInterface] = None
_global_prepare_health_monitor: Optional[PrepareMetricsHealthMonitor] = None


def get_global_prepare_metrics_collector() -> PrepareMetricsCollectorInterface:
    """Get global prepare metrics collector instance"""
    global _global_prepare_metrics_collector
    if _global_prepare_metrics_collector is None:
        _global_prepare_metrics_collector = create_prepare_in_memory_metrics_collector()
    return _global_prepare_metrics_collector


def set_global_prepare_metrics_collector(collector: PrepareMetricsCollectorInterface):
    """Set global prepare metrics collector instance"""
    global _global_prepare_metrics_collector
    _global_prepare_metrics_collector = collector


def get_global_prepare_health_monitor() -> PrepareMetricsHealthMonitor:
    """Get global prepare health monitor instance"""
    global _global_prepare_health_monitor
    if _global_prepare_health_monitor is None:
        _global_prepare_health_monitor = create_prepare_metrics_health_monitor(get_global_prepare_metrics_collector())
    return _global_prepare_health_monitor


def set_global_prepare_health_monitor(monitor: PrepareMetricsHealthMonitor):
    """Set global prepare health monitor instance"""
    global _global_prepare_health_monitor
    _global_prepare_health_monitor = monitor
