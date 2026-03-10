"""
MetaLearningObservability - Observability and metrics for Meta-Learning system.

[PHASE 7] Full Deployment with Observability

Provides:
- Comprehensive metrics collection
- Performance monitoring
- Health checks
- Telemetry aggregation
- Dashboard-ready statistics
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from agentic_core.L1_cognition.types.observability_types import (
    HealthStatus,
    MetricPoint,
)

Logger = logging.getLogger(__name__)


# Module-level singleton
_observability_instance: Any = None


@dataclass
class MetaLearningObservability:
    """
    Observability layer for Meta-Learning system.

    [PHASE 7] Core Implementation

    Features:
    - Real-time metrics collection
    - Component health monitoring
    - Performance tracking
    - Telemetry aggregation
    """

    # Metrics storage
    _metrics: list[MetricPoint] = field(default_factory=list)
    _max_metrics: int = 10000

    # Health status
    _health_status: dict[str, HealthStatus] = field(default_factory=dict)

    # Performance tracking
    _operation_times: dict[str, list[float]] = field(default_factory=dict)
    _max_operation_samples: int = 100

    # Aggregated stats
    stats: dict[str, Any] = field(
        default_factory=lambda: {
            "total_operations": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "pattern_stores": 0,
            "pattern_recalls": 0,
            "healing_operations": 0,
            "cross_domain_shares": 0,
            "errors": 0,
            "start_time": datetime.now().isoformat(),
        },
    )

    def __post_init__(self) -> None:
        """Initialize observability components."""
        self._initialize_health_checks()
        Logger.info("[MetaLearningObservability] Initialized")

    def _initialize_health_checks(self) -> None:
        """Initialize health check entries for all components."""
        components = [
            "MetaLearningClient",
            "HealingMemoryEmbedder",
            "CacheStrategyManager",
            "DomainContextManager",
            "Redis",
            "Pinecone",
        ]
        for component in components:
            self._health_status[component] = HealthStatus(
                component=component,
                healthy=True,
                message="Not yet checked",
            )

    # ==================== METRICS ====================

    def record_metric(
        self,
        name: str,
        value: float,
        tags: dict[str, str] | None = None,
    ) -> None:
        """
        Record a metric data point.

        Args:
            name: Metric name
            value: Metric value
            tags: Optional tags for filtering
        """
        metric = MetricPoint(name=name, value=value, tags=tags or {})
        self._metrics.append(metric)

        # Trim if over limit
        if len(self._metrics) > self._max_metrics:
            self._metrics = self._metrics[-self._max_metrics :]

    def get_metrics(
        self,
        name: str | None = None,
        limit: int = 100,
    ) -> list[MetricPoint]:
        """
        Get recorded metrics.

        Args:
            name: Optional filter by metric name
            limit: Maximum number of metrics to return

        Returns:
            List of MetricPoint objects
        """
        if name:
            filtered = [m for m in self._metrics if m.name == name]
        else:
            filtered = self._metrics

        return filtered[-limit:]

    # ==================== HEALTH CHECKS ====================

    def check_health(self) -> dict[str, HealthStatus]:
        """
        Run health checks on all components.

        Returns:
            Dict mapping component name to HealthStatus
        """
        self._check_meta_learning_client()
        self._check_cache_strategy_manager()
        self._check_domain_context_manager()

        return self._health_status

    def _check_meta_learning_client(self) -> None:
        """Check MetaLearningClient health."""
        try:
            from agentic_core.L1_cognition.reasoning.meta_learning_client_types import (
                get_meta_learning_client,
            )

            client = get_meta_learning_client()
            stats = client.get_stats()

            self._health_status["MetaLearningClient"] = HealthStatus(
                component="MetaLearningClient",
                healthy=True,
                message="Operational",
                details={"cache_size": stats.get("local_cache_size", 0)},
            )

            # Check Redis
            redis_available = stats.get("redis_available", False)
            self._health_status["Redis"] = HealthStatus(
                component="Redis",
                healthy=redis_available,
                message="Connected" if redis_available else "Unavailable (using fallback)",
            )

            # Check Pinecone
            pinecone_available = stats.get("pinecone_available", False)
            self._health_status["Pinecone"] = HealthStatus(
                component="Pinecone",
                healthy=pinecone_available,
                message="Connected" if pinecone_available else "Unavailable",
            )

        except Exception as e:
            # TODO: Handle specific exception properly
            raise  # Re-raise after logging/handling
            self._health_status["MetaLearningClient"] = HealthStatus(
                component="MetaLearningClient",
                healthy=False,
                message=f"Error: {e}",
            )

    def _check_cache_strategy_manager(self) -> None:
        """Check CacheStrategyManager health."""
        try:
            from agentic_core.L1_cognition.reasoning.cache_strategy_manager_types import (
                get_cache_strategy_manager,
            )

            manager = get_cache_strategy_manager()
            stats = manager.get_stats()

            self._health_status["CacheStrategyManager"] = HealthStatus(
                component="CacheStrategyManager",
                healthy=True,
                message="Operational",
                details={"domains_configured": len(stats.get("domain_configs", {}))},
            )

        except Exception as e:
            # TODO: Handle specific exception properly
            raise  # Re-raise after logging/handling
            self._health_status["CacheStrategyManager"] = HealthStatus(
                component="CacheStrategyManager",
                healthy=False,
                message=f"Error: {e}",
            )

    def _check_domain_context_manager(self) -> None:
        """Check DomainContextManager health."""
        try:
            from agentic_core.L1_cognition.reasoning.domain_context_manager_types import (
                get_domain_context_manager,
            )

            manager = get_domain_context_manager()
            stats = manager.get_stats()

            self._health_status["DomainContextManager"] = HealthStatus(
                component="DomainContextManager",
                healthy=True,
                message="Operational",
                details={"registered_domains": stats.get("registered_domains", [])},
            )

        except Exception as e:
            # TODO: Handle specific exception properly
            raise  # Re-raise after logging/handling
            self._health_status["DomainContextManager"] = HealthStatus(
                component="DomainContextManager",
                healthy=False,
                message=f"Error: {e}",
            )

    def get_health_summary(self) -> dict[str, Any]:
        """
        Get a summary of system health.

        Returns:
            Dict with overall health status and component details
        """
        self.check_health()

        healthy_count = sum(1 for s in self._health_status.values() if s.healthy)
        total_count = len(self._health_status)

        return {
            "overall_healthy": healthy_count == total_count,
            "healthy_components": healthy_count,
            "total_components": total_count,
            "components": {
                name: {
                    "healthy": status.healthy,
                    "message": status.message,
                    "last_check": status.last_check,
                }
                for name, status in self._health_status.items()
            },
        }

    # ==================== PERFORMANCE TRACKING ====================

    def record_operation_time(self, operation: str, duration_ms: float) -> None:
        """
        Record operation execution time.

        Args:
            operation: Operation name
            duration_ms: Duration in milliseconds
        """
        if operation not in self._operation_times:
            self._operation_times[operation] = []

        self._operation_times[operation].append(duration_ms)

        # Trim if over limit
        if len(self._operation_times[operation]) > self._max_operation_samples:
            self._operation_times[operation] = self._operation_times[operation][
                -self._max_operation_samples :
            ]

        # Update stats
        self.stats["total_operations"] += 1

    def get_operation_stats(self, operation: str | None = None) -> dict[str, Any]:
        """
        Get operation performance statistics.

        Args:
            operation: Optional specific operation to get stats for

        Returns:
            Dict with performance statistics
        """
        if operation:
            times = self._operation_times.get(operation, [])
            if not times:
                return {"operation": operation, "samples": 0}

            return {
                "operation": operation,
                "samples": len(times),
                "avg_ms": sum(times) / len(times),
                "min_ms": min(times),
                "max_ms": max(times),
                "p50_ms": sorted(times)[len(times) // 2] if times else 0,
                "p95_ms": sorted(times)[int(len(times) * 0.95)] if times else 0,
            }

        # All operations
        return {op: self.get_operation_stats(op) for op in self._operation_times.keys()}

    # ==================== STAT TRACKING ====================

    def increment_stat(self, stat_name: str, amount: int = 1) -> None:
        """Increment a statistic counter."""
        if stat_name in self.stats:
            self.stats[stat_name] += amount

    def get_stats(self) -> dict[str, Any]:
        """Get all statistics."""
        return {
            **self.stats,
            "uptime_seconds": self._calculate_uptime(),
            "metrics_count": len(self._metrics),
            "operations_tracked": len(self._operation_times),
        }

    def _calculate_uptime(self) -> float:
        """Calculate system uptime in seconds."""
        try:
            start = datetime.fromisoformat(self.stats["start_time"])
            return (datetime.now() - start).total_seconds()
        except Exception:
            return 0.0

    # ==================== DASHBOARD DATA ====================

    def get_dashboard_data(self) -> dict[str, Any]:
        """
        Get comprehensive data for dashboard display.

        Returns:
            Dict with all dashboard-relevant data
        """
        return {
            "health": self.get_health_summary(),
            "stats": self.get_stats(),
            "performance": self.get_operation_stats(),
            "recent_metrics": [
                {"name": m.name, "value": m.value, "timestamp": m.timestamp}
                for m in self.get_metrics(limit=LIMIT)
            ],
        }

    @classmethod
    def reset_instance(cls) -> None:
        """[TESTING ONLY] Reset singleton state."""
        global _observability_instance
        _observability_instance = None


def get_meta_learning_observability() -> MetaLearningObservability:
    """Get or create the MetaLearningObservability singleton."""
    global _observability_instance
    if _observability_instance is None:
        _observability_instance = MetaLearningObservability()
    return _observability_instance


class OperationTimer:
    """Context manager for timing operations."""

    def __init__(self, operation: str):
        self.operation = operation
        self.start_time: float = 0

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.time() - self.start_time) * 1000
        observability = get_meta_learning_observability()
        observability.record_operation_time(self.operation, duration_ms)
        return False
