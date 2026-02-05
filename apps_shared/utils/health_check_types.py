"""
Health Check Utilities - Application health and readiness checks.

Provides health endpoints, dependency checks, and deployment readiness
validation for apps_lic and apps_rg.
Phase 5B - Deployment Readiness
"""

from __future__ import annotations

import logging
import os
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Health check status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class CheckResult:
    """Result of a single health check."""

    name: str
    status: HealthStatus
    message: str = ""
    duration_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_healthy(self) -> bool:
        return self.status == HealthStatus.HEALTHY

    @property
    def is_critical(self) -> bool:
        return self.status == HealthStatus.UNHEALTHY


@dataclass
class HealthReport:
    """Complete health report."""

    status: HealthStatus
    checks: list[CheckResult]
    timestamp: float = field(default_factory=time.time)
    version: str = "1.0.0"

    @property
    def is_healthy(self) -> bool:
        return self.status == HealthStatus.HEALTHY

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "status": self.status.value,
            "timestamp": self.timestamp,
            "version": self.version,
            "checks": [
                {
                    "name": c.name,
                    "status": c.status.value,
                    "message": c.message,
                    "duration_ms": round(c.duration_ms, 2),
                    "metadata": c.metadata,
                }
                for c in self.checks
            ],
        }


class HealthChecker:
    """Manages health checks for the application."""

    def __init__(self, app_name: str = "app", version: str = "1.0.0"):
        self.app_name = app_name
        self.version = version
        self._checks: dict[str, tuple[Callable[[], CheckResult], bool]] = {}

    def register_check(
        self,
        name: str,
        check_fn: Callable[[], CheckResult],
        critical: bool = False,
    ) -> None:
        """
        Register a health check.

        Args:
            name: Check name
            check_fn: Function that performs the check
            critical: If True, failure makes entire app unhealthy
        """
        self._checks[name] = (check_fn, critical)
        logger.info(f"Registered health check: {name} (critical={critical})")

    def unregister_check(self, name: str) -> bool:
        """Unregister a health check."""
        if name in self._checks:
            del self._checks[name]
            return True
        return False

    def run_check(self, name: str) -> CheckResult | None:
        """Run a specific health check."""
        if name not in self._checks:
            return None

        check_fn, _ = self._checks[name]
        start = time.perf_counter()

        try:
            result = check_fn()
            result.duration_ms = (time.perf_counter() - start) * 1000
            return result
        except Exception as e:
            return CheckResult(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Check failed with error: {e}",
                duration_ms=(time.perf_counter() - start) * 1000,
            )

    def run_all_checks(self) -> HealthReport:
        """Run all registered health checks."""
        results: list[CheckResult] = []
        overall_status = HealthStatus.HEALTHY

        for name, (check_fn, critical) in self._checks.items():
            result = self.run_check(name)
            if result:
                results.append(result)

                if result.status == HealthStatus.UNHEALTHY and critical:
                    overall_status = HealthStatus.UNHEALTHY
                elif result.status == HealthStatus.DEGRADED:
                    if overall_status == HealthStatus.HEALTHY:
                        overall_status = HealthStatus.DEGRADED
                elif result.status == HealthStatus.UNHEALTHY:
                    if overall_status == HealthStatus.HEALTHY:
                        overall_status = HealthStatus.DEGRADED

        return HealthReport(
            status=overall_status,
            checks=results,
            version=self.version,
        )

    def get_liveness(self) -> CheckResult:
        """Simple liveness check - is the app running?"""
        return CheckResult(
            name="liveness",
            status=HealthStatus.HEALTHY,
            message="Application is alive",
        )

    def get_readiness(self) -> HealthReport:
        """Full readiness check - is the app ready to serve traffic?"""
        return self.run_all_checks()


# Common health check factories
class CommonChecks:
    """Factory for common health checks."""

    @staticmethod
    def env_var_check(var_name: str, required: bool = True) -> Callable[[], CheckResult]:
        """Create a check for an environment variable."""

        def check() -> CheckResult:
            value = os.getenv(var_name)
            if value:
                return CheckResult(
                    name=f"env:{var_name}",
                    status=HealthStatus.HEALTHY,
                    message=f"{var_name} is set",
                )
            elif required:
                return CheckResult(
                    name=f"env:{var_name}",
                    status=HealthStatus.UNHEALTHY,
                    message=f"{var_name} is not set",
                )
            else:
                return CheckResult(
                    name=f"env:{var_name}",
                    status=HealthStatus.DEGRADED,
                    message=f"{var_name} is not set (optional)",
                )

        return check

    @staticmethod
    def redis_check(
        host: str = "localhost",
        port: int = 6379,
    ) -> Callable[[], CheckResult]:
        """Create a Redis connectivity check."""

        def check() -> CheckResult:
            try:
                import redis

                client = redis.Redis(host=host, port=port, socket_timeout=2)
                client.ping()
                return CheckResult(
                    name="redis",
                    status=HealthStatus.HEALTHY,
                    message=f"Redis connected at {host}:{port}",
                )
            except ImportError:
                return CheckResult(
                    name="redis",
                    status=HealthStatus.DEGRADED,
                    message="Redis client not installed",
                )
            except Exception as e:
                return CheckResult(
                    name="redis",
                    status=HealthStatus.UNHEALTHY,
                    message=f"Redis connection failed: {e}",
                )

        return check

    @staticmethod
    def disk_space_check(
        path: str = "/",
        min_free_gb: float = 1.0,
    ) -> Callable[[], CheckResult]:
        """Create a disk space check."""

        def check() -> CheckResult:
            try:
                import shutil

                total, used, free = shutil.disk_usage(path)
                free_gb = free / (1024**3)

                if free_gb >= min_free_gb:
                    return CheckResult(
                        name="disk_space",
                        status=HealthStatus.HEALTHY,
                        message=f"{free_gb:.2f} GB free",
                        metadata={"free_gb": round(free_gb, 2)},
                    )
                else:
                    return CheckResult(
                        name="disk_space",
                        status=HealthStatus.DEGRADED,
                        message=f"Low disk space: {free_gb:.2f} GB free",
                        metadata={"free_gb": round(free_gb, 2)},
                    )
            except Exception as e:
                return CheckResult(
                    name="disk_space",
                    status=HealthStatus.UNKNOWN,
                    message=f"Could not check disk space: {e}",
                )

        return check

    @staticmethod
    def memory_check(max_percent: float = 90.0) -> Callable[[], CheckResult]:
        """Create a memory usage check."""

        def check() -> CheckResult:
            try:
                import psutil

                memory = psutil.virtual_memory()
                percent = memory.percent

                if percent < max_percent:
                    return CheckResult(
                        name="memory",
                        status=HealthStatus.HEALTHY,
                        message=f"Memory usage: {percent:.1f}%",
                        metadata={"percent": percent},
                    )
                else:
                    return CheckResult(
                        name="memory",
                        status=HealthStatus.DEGRADED,
                        message=f"High memory usage: {percent:.1f}%",
                        metadata={"percent": percent},
                    )
            except ImportError:
                return CheckResult(
                    name="memory",
                    status=HealthStatus.UNKNOWN,
                    message="psutil not installed",
                )
            except Exception as e:
                return CheckResult(
                    name="memory",
                    status=HealthStatus.UNKNOWN,
                    message=f"Could not check memory: {e}",
                )

        return check


class ReadinessGate:
    """Controls application readiness state."""

    def __init__(self):
        self._ready = False
        self._reason: str = "Not initialized"

    def set_ready(self) -> None:
        """Mark application as ready."""
        self._ready = True
        self._reason = "Ready"
        logger.info("Application marked as ready")

    def set_not_ready(self, reason: str) -> None:
        """Mark application as not ready."""
        self._ready = False
        self._reason = reason
        logger.warning(f"Application marked as not ready: {reason}")

    def is_ready(self) -> bool:
        """Check if application is ready."""
        return self._ready

    def get_status(self) -> dict[str, Any]:
        """Get readiness status."""
        return {
            "ready": self._ready,
            "reason": self._reason,
        }


# Global instances
_health_checker: HealthChecker | None = None
_readiness_gate: ReadinessGate | None = None


def get_health_checker() -> HealthChecker:
    """Get the global health checker."""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker


def get_readiness_gate() -> ReadinessGate:
    """Get the global readiness gate."""
    global _readiness_gate
    if _readiness_gate is None:
        _readiness_gate = ReadinessGate()
    return _readiness_gate
