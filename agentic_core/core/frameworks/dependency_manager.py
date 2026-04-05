"""Dependency management framework for runtime dependency handling.

This framework provides circuit breaker patterns and explicit failure modes
for RUNTIME dependencies (services, databases, external APIs). It is NOT
intended as a direct replacement for import-time dependency handling.

For import-time dependencies (like tqdm, FAISS, etc.), use explicit
try/except patterns with specific exception types and logging, as demonstrated
in the Phase 2 fixes to _ssot_phases.py, execute_ssot.py, etc.

Usage:
    # For runtime services
    manager = DependencyManager()
    manager.register_dependency("database", DatabaseConnection, health_check=is_db_healthy)

    # For import-time dependencies, use explicit try/except:
    try:
        from tqdm import tqdm
        _TQDM_AVAILABLE = True
    except ImportError as e:
        _TQDM_AVAILABLE = False
        logger.warning(f"tqdm not available: {e}. Install with: pip install tqdm")
        # Define fallback implementation
        class tqdm: ...
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    emit_determinism_digest,
    emit_replay_key,
)

emit_replay_key("p0", "dependency_manager")
emit_determinism_digest("p0", "dependency_manager")

Logger = logging.getLogger(__name__)


class DependencyStatus(Enum):
    """Status of a dependency."""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    DEGRADED = "degraded"
    CIRCUIT_OPEN = "circuit_open"


@dataclass
class DependencyInfo:
    """Information about a dependency."""

    name: str
    status: DependencyStatus
    version: str | None = None
    error_message: str | None = None
    last_check: float | None = None
    failure_count: int = 0
    circuit_breaker_threshold: int = 5


class DependencyError(Exception):
    """Explicit error for missing or unavailable dependencies."""

    def __init__(self, message: str, dependency_name: str, suggestion: str | None = None):
        super().__init__(message)
        self.dependency_name = dependency_name
        self.suggestion = suggestion


class CircuitBreakerError(Exception):
    """Error raised when circuit breaker is open."""

    def __init__(self, dependency_name: str, failure_count: int):
        super().__init__(f"Circuit breaker open for {dependency_name} after {failure_count} failures")
        self.dependency_name = dependency_name
        self.failure_count = failure_count


class HealthCheckable(Protocol):
    """Protocol for components that can be health-checked."""

    def health_check(self) -> bool:
        """Check if the component is healthy."""
        ...


class DependencyManager:
    """Manages dependencies with explicit failure modes and circuit breaking."""

    def __init__(self):
        """Initialize dependency manager."""
        self._dependencies: dict[str, DependencyInfo] = {}
        self._instances: dict[str, Any] = {}
        self._health_checks: dict[str, callable] = {}
        self._circuit_breakers: dict[str, dict[str, Any]] = {}

    def register_dependency(
        self,
        name: str,
        health_check: callable | None = None,
        circuit_breaker_threshold: int = 5,
        fallback_instance: Any | None = None,
    ) -> None:
        """Register a dependency with optional health check and circuit breaker."""
        self._dependencies[name] = DependencyInfo(
            name=name,
            status=DependencyStatus.UNAVAILABLE,
            circuit_breaker_threshold=circuit_breaker_threshold,
        )

        if health_check:
            self._health_checks[name] = health_check

        if fallback_instance:
            self._instances[name] = fallback_instance

        self._circuit_breakers[name] = {
            "failure_count": 0,
            "last_failure_time": None,
            "state": "closed",  # closed, open, half_open
        }

    def check_dependency(self, name: str) -> DependencyInfo:
        """Check the status of a dependency."""
        import time

        if name not in self._dependencies:
            raise DependencyError(f"Dependency '{name}' not registered", name)

        dependency = self._dependencies[name]
        circuit_breaker = self._circuit_breakers[name]

        # Check circuit breaker
        if circuit_breaker["state"] == "open":
            dependency.status = DependencyStatus.CIRCUIT_OPEN
            return dependency

        # Perform health check if available
        if name in self._health_checks:
            try:
                is_healthy = self._health_checks[name]()
                dependency.status = DependencyStatus.AVAILABLE if is_healthy else DependencyStatus.UNAVAILABLE
                dependency.last_check = time.time()

                if not is_healthy:
                    self._record_failure(name)
                else:
                    # Reset failure count on success
                    circuit_breaker["failure_count"] = 0
                    if circuit_breaker["state"] == "half_open":
                        circuit_breaker["state"] = "closed"

            except Exception as e:
                dependency.status = DependencyStatus.UNAVAILABLE
                dependency.error_message = str(e)
                dependency.last_check = time.time()
                self._record_failure(name)
        else:
            # No health check available, assume available
            dependency.status = DependencyStatus.AVAILABLE

        return dependency

    def get_dependency(self, name: str) -> Any:
        """Get a dependency instance, raising explicit errors if unavailable."""
        dependency = self.check_dependency(name)

        if dependency.status == DependencyStatus.CIRCUIT_OPEN:
            raise CircuitBreakerError(name, self._circuit_breakers[name]["failure_count"])

        if dependency.status != DependencyStatus.AVAILABLE:
            suggestion = self._get_suggestion(name)
            raise DependencyError(f"Dependency '{name}' is {dependency.status.value}", name, suggestion)

        # Return cached instance or create new one
        if name in self._instances:
            return self._instances[name]

        # Try to import and instantiate
        try:
            instance = self._create_instance(name)
            self._instances[name] = instance
            return instance
        except Exception as e:
            self._record_failure(name)
            suggestion = self._get_suggestion(name)
            raise DependencyError(f"Failed to create instance of '{name}': {e}", name, suggestion)

    def _create_instance(self, name: str) -> Any:
        """Create an instance of the dependency."""
        # This would be customized based on the specific dependency
        # For now, try to import the module
        import importlib

        module_name = name.replace("-", "_").replace(".", "_")
        module = importlib.import_module(module_name)

        # Look for a class with the same name
        class_name = name.split(".")[-1].replace("-", "_").title()
        if hasattr(module, class_name):
            return getattr(module, class_name)()

        # Return the module itself
        return module

    def _record_failure(self, name: str) -> None:
        """Record a failure for circuit breaker tracking."""
        if name not in self._circuit_breakers:
            return

        circuit_breaker = self._circuit_breakers[name]
        if circuit_breaker["state"] == "open":
            return

        circuit_breaker["failure_count"] += 1
        circuit_breaker["last_failure_time"] = time.time()

        dependency = self._dependencies[name]
        dependency.failure_count = circuit_breaker["failure_count"]

        # Open circuit if threshold exceeded
        if circuit_breaker["failure_count"] >= dependency.circuit_breaker_threshold:
            circuit_breaker["state"] = "open"
            dependency.status = DependencyStatus.CIRCUIT_OPEN
            Logger.warning(
                f"Circuit breaker opened for {name} after {circuit_breaker['failure_count']} failures"
            )

    def _get_suggestion(self, name: str) -> str:
        """Get suggestion for resolving dependency issue."""
        suggestions = {
            "mcp11": "Install the Memory MCP server or run in CLI context",
            "sqlite-memory-store": "Install with: pip install sqlite-memory-store",
            "pydantic": "Install with: pip install pydantic",
            "semantic-cache": "Install with: pip install semantic-cache",
            "embedding-mixin": "Install with: pip install embedding-mixin",
        }

        return suggestions.get(name, f"Check installation and availability of '{name}'")

    def get_all_dependencies_status(self) -> dict[str, DependencyInfo]:
        """Get status of all registered dependencies."""
        return {name: self.check_dependency(name) for name in self._dependencies}

    def reset_circuit_breaker(self, name: str) -> None:
        """Reset circuit breaker for a dependency."""
        if name in self._circuit_breakers:
            self._circuit_breakers[name] = {"failure_count": 0, "last_failure_time": None, "state": "closed"}
            self._dependencies[name].status = DependencyStatus.UNAVAILABLE


# Global dependency manager instance
_dependency_manager = DependencyManager()


def get_dependency_manager() -> DependencyManager:
    """Get the global dependency manager instance."""
    return _dependency_manager


def register_dependency(
    name: str,
    health_check: callable | None = None,
    circuit_breaker_threshold: int = 5,
    fallback_instance: Any | None = None,
) -> None:
    """Register a dependency with the global manager."""
    _dependency_manager.register_dependency(name, health_check, circuit_breaker_threshold, fallback_instance)


def get_dependency(name: str) -> Any:
    """Get a dependency from the global manager."""
    return _dependency_manager.get_dependency(name)


def check_dependency(name: str) -> DependencyInfo:
    """Check dependency status from the global manager."""
    return _dependency_manager.check_dependency(name)


# Decorator for explicit dependency injection
def requires_dependency(name: str, fallback: Any | None = None):
    """Decorator to explicitly declare dependency requirements."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                dependency = get_dependency(name)
                kwargs[f"_{name}_dependency"] = dependency
                return func(*args, **kwargs)
            except (DependencyError, CircuitBreakerError) as e:
                if fallback is not None:
                    kwargs[f"_{name}_dependency"] = fallback
                    return func(*args, **kwargs)
                else:
                    raise e

        return wrapper

    return decorator


# Context manager for optional dependencies
class OptionalDependency:
    """Context manager for optional dependencies."""

    def __init__(self, name: str, fallback: Any | None = None):
        self.name = name
        self.fallback = fallback
        self.dependency = None

    def __enter__(self) -> Any:
        try:
            self.dependency = get_dependency(self.name)
            return self.dependency
        except (DependencyError, CircuitBreakerError):
            if self.fallback is not None:
                return self.fallback
            return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False  # Don't suppress exceptions
