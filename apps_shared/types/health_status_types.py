"""Health Check Aggregation - System-wide health monitoring.

This module provides a centralized health check system that aggregates
the status of all hardened components to provide a single view of
system health for operations teams.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "health_status_types", "p0_governance")
_emit_reads_policy_state("p0", "health_status_types", "policy_binding")
_emit_snapshots_state("p0", "health_status_types", "state_snapshot")
emit_replay_key("p0", "health_status_types")
emit_determinism_digest("p0", "health_status_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Health status levels."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class ComponentType(str, Enum):
    """Types of components being monitored."""

    BULKHEAD = "bulkhead"
    CIRCUIT_BREAKER = "circuit_breaker"
    DEAD_LETTER_QUEUE = "dead_letter_queue"
    CHECKPOINT_MANAGER = "checkpoint_manager"
    RETRY_POLICY = "retry_policy"
    PIPELINE = "pipeline"
    CUSTOM = "custom"


@dataclass
class HealthCheckResult:
    """Result of a health check."""

    component_name: str
    component_type: ComponentType
    status: HealthStatus
    message: str
    timestamp: datetime
    metrics: dict[str, Any] = field(default_factory=dict)
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "component": self.component_name,
            "type": self.component_type.value,
            "status": self.status.value,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "metrics": self.metrics,
            "details": self.details,
        }


class HealthChecker(ABC):
    """Abstract base for health checkers."""

    @abstractmethod
    async def check_health(self) -> HealthCheckResult:
        """Perform health check.

        Returns:
            Health check result
        """
        pass

    @property
    @abstractmethod
    def component_name(self) -> str:
        """Get component name."""
        pass

    @property
    @abstractmethod
    def component_type(self) -> ComponentType:
        """Get component type."""
        pass


class BulkheadHealthChecker(HealthChecker):
    """Health checker for bulkheads."""

    def __init__(self, bulkhead_manager):
        """Initialize bulkhead health checker.

        Args:
            bulkhead_manager: BulkheadManager instance
        """
        self.bulkhead_manager = bulkhead_manager

    async def check_health(self) -> HealthCheckResult:
        """Check bulkhead health.

        Returns:
            Health check result
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "BulkheadHealthChecker.check_health")
        try:
            metrics = self.bulkhead_manager.get_all_metrics()
            issues = []
            metrics["global"]["total_active_tasks"]
            metrics["global"]["total_queued_tasks"]
            for name, bulkhead_metrics in metrics["bulkheads"].items():
                utilization = bulkhead_metrics.utilization_percent
                if utilization > 90:
                    issues.append(f"{name}: High utilization ({utilization:.1f}%)")
                if bulkhead_metrics.queued_tasks > bulkhead_metrics.queue_size * 0.8:
                    issues.append(
                        f"{name}: Queue buildup ({bulkhead_metrics.queued_tasks}/{bulkhead_metrics.queue_size})"
                    )
            if not issues:
                status = HealthStatus.HEALTHY
                message = "All bulkheads operating normally"
            elif len(issues) <= 2:
                status = HealthStatus.DEGRADED
                message = f"Minor issues: {'; '.join(issues[:2])}"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Multiple issues: {'; '.join(issues[:3])}"
            return HealthCheckResult(
                component_name=self.component_name,
                component_type=self.component_type,
                status=status,
                message=message,
                timestamp=datetime.utcnow(),
                metrics=metrics,
            )
        # guardian: allow-silent-swallow
        except Exception as e:
            return HealthCheckResult(
                component_name=self.component_name,
                component_type=self.component_type,
                status=HealthStatus.CRITICAL,
                message=f"Health check failed: {e}",
                timestamp=datetime.utcnow(),
            )

    @property
    def component_name(self) -> str:
        """Get component name."""
        return "bulkhead_manager"

    @property
    def component_type(self) -> ComponentType:
        """Get component type."""
        return ComponentType.BULKHEAD


class CircuitBreakerHealthChecker(HealthChecker):
    """Health checker for circuit breakers."""

    def __init__(self, circuit_breaker_registry):
        """Initialize circuit breaker health checker.

        Args:
            circuit_breaker_registry: CircuitBreakerRegistry instance
        """
        self.registry = circuit_breaker_registry

    async def check_health(self) -> HealthCheckResult:
        """Check circuit breaker health.

        Returns:
            Health check result
        """
        try:
            all_stats = self.registry.get_all_stats()
            open_circuits = []
            half_open_circuits = []
            high_failure_rates = []
            for name, stats in all_stats.items():
                state = stats["state"]
                if state == "open":
                    open_circuits.append(name)
                elif state == "half_open":
                    half_open_circuits.append(name)
                failure_rate = stats.get("current_failure_rate", 0)
                if failure_rate > 0.3:
                    high_failure_rates.append(f"{name}: {failure_rate:.1%}")
            if open_circuits:
                status = HealthStatus.CRITICAL
                message = f"Circuits open: {', '.join(open_circuits)}"
            elif half_open_circuits or high_failure_rates:
                status = HealthStatus.DEGRADED
                issues = half_open_circuits + high_failure_rates
                message = f"Issues detected: {'; '.join(issues[:3])}"
            else:
                status = HealthStatus.HEALTHY
                message = "All circuits closed and healthy"
            return HealthCheckResult(
                component_name=self.component_name,
                component_type=self.component_type,
                status=status,
                message=message,
                timestamp=datetime.utcnow(),
                metrics={
                    "total_circuits": len(all_stats),
                    "open_circuits": len(open_circuits),
                    "half_open_circuits": len(half_open_circuits),
                    "high_failure_rates": len(high_failure_rates),
                },
                details={"circuit_stats": all_stats},
            )
        # guardian: allow-silent-swallow
        except Exception as e:
            return HealthCheckResult(
                component_name=self.component_name,
                component_type=self.component_type,
                status=HealthStatus.CRITICAL,
                message=f"Health check failed: {e}",
                timestamp=datetime.utcnow(),
            )

    @property
    def component_name(self) -> str:
        """Get component name."""
        return "circuit_breaker_registry"

    @property
    def component_type(self) -> ComponentType:
        """Get component type."""
        return ComponentType.CIRCUIT_BREAKER


class DeadLetterQueueHealthChecker(HealthChecker):
    """Health checker for dead letter queue."""

    def __init__(self, dead_letter_queue):
        """Initialize DLQ health checker.

        Args:
            dead_letter_queue: DeadLetterQueue instance
        """
        self.dlq = dead_letter_queue

    async def check_health(self) -> HealthCheckResult:
        """Check DLQ health.

        Returns:
            Health check result
        """
        try:
            health = await self.dlq.health_check()
            pending = health["pending_review"]
            investigation = health["under_investigation"]
            total_pending = pending + investigation
            if total_pending > 100:
                status = HealthStatus.CRITICAL
                message = f"Dead letter queue overloaded: {total_pending} items pending"
            elif total_pending > 50:
                status = HealthStatus.UNHEALTHY
                message = f"Dead letter queue high: {total_pending} items pending"
            elif total_pending > 10:
                status = HealthStatus.DEGRADED
                message = f"Dead letter queue elevated: {total_pending} items pending"
            else:
                status = HealthStatus.HEALTHY
                message = f"Dead letter queue normal: {total_pending} items pending"
            return HealthCheckResult(
                component_name=self.component_name,
                component_type=self.component_type,
                status=status,
                message=message,
                timestamp=datetime.utcnow(),
                metrics=health,
            )
        # guardian: allow-silent-swallow
        except Exception as e:
            return HealthCheckResult(
                component_name=self.component_name,
                component_type=self.component_type,
                status=HealthStatus.CRITICAL,
                message=f"Health check failed: {e}",
                timestamp=datetime.utcnow(),
            )

    @property
    def component_name(self) -> str:
        """Get component name."""
        return "dead_letter_queue"

    @property
    def component_type(self) -> ComponentType:
        """Get component type."""
        return ComponentType.DEAD_LETTER_QUEUE


class CheckpointManagerHealthChecker(HealthChecker):
    """Health checker for checkpoint manager."""

    def __init__(self, checkpoint_manager):
        """Initialize checkpoint manager health checker.

        Args:
            checkpoint_manager: CheckpointManager instance
        """
        self.checkpoint_manager = checkpoint_manager

    async def check_health(self) -> HealthCheckResult:
        """Check checkpoint manager health.

        Returns:
            Health check result
        """
        try:
            test_trace_id = f"health_check_{int(time.time())}"
            test_envelope = TextEnvelope(text="health check test", trace_id=test_trace_id)
            save_success = await self.checkpoint_manager.save(test_envelope)
            loaded = await self.checkpoint_manager.load(test_trace_id)
            delete_success = await self.checkpoint_manager.delete(test_trace_id)
            stats = self.checkpoint_manager.get_stats()
            if save_success and loaded and delete_success:
                status = HealthStatus.HEALTHY
                message = "Checkpoint operations working normally"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Checkpoint operations failing (save:{save_success}, load:{loaded is not None}, delete:{delete_success})"
            return HealthCheckResult(
                component_name=self.component_name,
                component_type=self.component_type,
                status=status,
                message=message,
                timestamp=datetime.utcnow(),
                metrics=stats,
            )
        # guardian: allow-silent-swallow
        except Exception as e:
            return HealthCheckResult(
                component_name=self.component_name,
                component_type=self.component_type,
                status=HealthStatus.CRITICAL,
                message=f"Health check failed: {e}",
                timestamp=datetime.utcnow(),
            )

    @property
    def component_name(self) -> str:
        """Get component name."""
        return "checkpoint_manager"

    @property
    def component_type(self) -> ComponentType:
        """Get component type."""
        return ComponentType.CHECKPOINT_MANAGER


class HealthCheckRegistry:
    """Registry for managing health checks."""

    def __init__(self):
        """Initialize health check registry."""
        self.checkers: dict[str, HealthChecker] = {}
        self._lock = asyncio.Lock()
        self._last_check: datetime | None = None
        self._last_results: dict[str, HealthCheckResult] = {}

    async def register_checker(self, checker: HealthChecker) -> None:
        """Register a health checker.

        Args:
            checker: Health checker to register
        """
        async with self._lock:
            self.checkers[checker.component_name] = checker
            logger.debug(f"Registered health checker: {checker.component_name}")

    async def unregister_checker(self, component_name: str) -> None:
        """Unregister a health checker.

        Args:
            component_name: Component name to unregister
        """
        async with self._lock:
            if component_name in self.checkers:
                del self.checkers[component_name]
                logger.debug(f"Unregistered health checker: {component_name}")

    async def check_all(self) -> dict[str, Any]:
        """Check health of all registered components.

        Returns:
            Aggregated health results
        """
        async with self._lock:
            results = []
            overall_status = HealthStatus.HEALTHY
            critical_issues = []
            tasks = []
            for checker in self.checkers.values():
                task = asyncio.create_task(self._safe_check(checker))
                tasks.append(task)
            if tasks:
                checker_results = await asyncio.gather(*tasks, return_exceptions=True)
                for result in checker_results:
                    if isinstance(result, Exception):
                        error_result = HealthCheckResult(
                            component_name="unknown",
                            component_type=ComponentType.CUSTOM,
                            status=HealthStatus.CRITICAL,
                            message=f"Health check error: {result}",
                            timestamp=datetime.utcnow(),
                        )
                        results.append(error_result)
                        critical_issues.append(str(result))
                    else:
                        results.append(result)
                        if result.status == HealthStatus.CRITICAL:
                            overall_status = HealthStatus.CRITICAL
                            critical_issues.append(result.message)
                        elif (
                            result.status == HealthStatus.UNHEALTHY
                            and overall_status != HealthStatus.CRITICAL
                        ):
                            overall_status = HealthStatus.UNHEALTHY
                        elif result.status == HealthStatus.DEGRADED and overall_status not in [
                            HealthStatus.CRITICAL,
                            HealthStatus.UNHEALTHY,
                        ]:
                            overall_status = HealthStatus.DEGRADED
            self._last_check = datetime.utcnow()
            self._last_results = {r.component_name: r for r in results}
            response = {
                "status": overall_status.value,
                "timestamp": self._last_check.isoformat(),
                "components": [r.to_dict() for r in results],
                "summary": {
                    "total_components": len(results),
                    "healthy": sum(1 for r in results if r.status == HealthStatus.HEALTHY),
                    "degraded": sum(1 for r in results if r.status == HealthStatus.DEGRADED),
                    "unhealthy": sum(1 for r in results if r.status == HealthStatus.UNHEALTHY),
                    "critical": sum(1 for r in results if r.status == HealthStatus.CRITICAL),
                },
            }
            if critical_issues:
                response["critical_issues"] = critical_issues[:5]
            return response

    async def _safe_check(self, checker: HealthChecker) -> HealthCheckResult:
        """Safely execute health check.

        Args:
            checker: Health checker to execute

        Returns:
            Health check result
        """
        try:
            return await checker.check_health()
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Health check failed for {checker.component_name}: {e}")
            return HealthCheckResult(
                component_name=checker.component_name,
                component_type=checker.component_type,
                status=HealthStatus.CRITICAL,
                message=f"Health check failed: {e}",
                timestamp=datetime.utcnow(),
            )

    async def check_component(self, component_name: str) -> HealthCheckResult | None:
        """Check health of specific component.

        Args:
            component_name: Component to check

        Returns:
            Health check result if found
        """
        async with self._lock:
            checker = self.checkers.get(component_name)
            if not checker:
                return None
            return await self._safe_check(checker)

    def list_components(self) -> list[str]:
        """List all registered components.

        Returns:
            List of component names
        """
        return list(self.checkers.keys())

    def get_last_results(self) -> dict[str, HealthCheckResult]:
        """Get results from last health check.

        Returns:
            Last health check results
        """
        return self._last_results.copy()


_health_registry: HealthCheckRegistry | None = None
_registry_lock = asyncio.Lock()


async def get_health_registry() -> HealthCheckRegistry:
    """Get global health check registry.

    Returns:
        HealthCheckRegistry instance
    """
    global _health_registry
    async with _registry_lock:
        if _health_registry is None:
            _health_registry = HealthCheckRegistry()
    return _health_registry


async def initialize_system_health_checks(
    bulkhead_manager=None, circuit_breaker_registry=None, dead_letter_queue=None, checkpoint_manager=None
) -> None:
    """Initialize health checks for all system components.

    Args:
        bulkhead_manager: BulkheadManager instance
        circuit_breaker_registry: CircuitBreakerRegistry instance
        dead_letter_queue: DeadLetterQueue instance
        checkpoint_manager: CheckpointManager instance
    """
    registry = await get_health_registry()
    if bulkhead_manager:
        await registry.register_checker(BulkheadHealthChecker(bulkhead_manager))
    if circuit_breaker_registry:
        await registry.register_checker(CircuitBreakerHealthChecker(circuit_breaker_registry))
    if dead_letter_queue:
        await registry.register_checker(DeadLetterQueueHealthChecker(dead_letter_queue))
    if checkpoint_manager:
        await registry.register_checker(CheckpointManagerHealthChecker(checkpoint_manager))
    logger.info(f"Initialized health checks for {len(registry.list_components())} components")
