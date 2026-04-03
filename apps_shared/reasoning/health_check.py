"""Health Check - Stub implementation for reasoning compatibility."""
from enum import Enum
from dataclasses import dataclass
from typing import Any


class HealthStatus(Enum):
    """Health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


class ComponentType(Enum):
    """Component type."""
    DATABASE = "database"
    SERVICE = "service"
    CUSTOM = "custom"


@dataclass
class HealthCheckResult:
    """Health check result."""
    component_name: str
    component_type: ComponentType
    status: HealthStatus
    message: str
    timestamp: Any = None
    metrics: dict[str, Any] | None = None


class HealthChecker:
    """Base health checker."""

    async def check_health(self) -> HealthCheckResult:
        """Check health."""
        raise NotImplementedError

    @property
    def component_name(self) -> str:
        """Component name."""
        raise NotImplementedError

    @property
    def component_type(self) -> ComponentType:
        """Component type."""
        raise NotImplementedError


class HealthCheckRegistry:
    """Health check registry."""

    def __init__(self):
        self._checkers: list[HealthChecker] = []

    async def register_checker(self, checker: HealthChecker) -> None:
        """Register checker."""
        self._checkers.append(checker)

    async def check_all(self) -> dict[str, Any]:
        """Run all health checks."""
        results = {}
        for checker in self._checkers:
            result = await checker.check_health()
            results[checker.component_name] = {
                "status": result.status.value,
                "message": result.message,
            }
        return results


_registry: HealthCheckRegistry | None = None


async def get_health_registry() -> HealthCheckRegistry:
    """Get global health check registry."""
    global _registry
    if _registry is None:
        _registry = HealthCheckRegistry()
    return _registry


async def initialize_system_health_checks(**kwargs) -> None:
    """Initialize system health checks."""
    pass


__all__ = [
    "HealthStatus",
    "ComponentType",
    "HealthCheckResult",
    "HealthChecker",
    "HealthCheckRegistry",
    "get_health_registry",
    "initialize_system_health_checks",
]
