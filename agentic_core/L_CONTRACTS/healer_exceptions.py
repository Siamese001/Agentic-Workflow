"""
HealerError - Domain exceptions for sovereign healing operations.

Defines custom exceptions used by HealerMixin and related healing agents.
"""

from __future__ import annotations

from typing import Any


class HealerError(Exception):
    """
    Base exception for all healing-related errors.

    Raised when a healing operation fails due to invalid state,
    configuration issues, or other healing-specific problems.
    """

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            details_str = ", ".join((f"{k}={v}" for k, v in self.details.items()))
            return f"{self.message} ({details_str})"
        return self.message


class CircularDependencyError(HealerError):
    """
    Raised when a circular dependency is detected during healing operations.

    This can occur when agents recursively call each other's heal methods
    without proper cycle detection.
    """

    def __init__(self, cycle_path: list[str]):
        message = f"Circular dependency detected: {' -> '.join(cycle_path)} -> {cycle_path[0]}"
        super().__init__(message, {"cycle_path": cycle_path})
        self.cycle_path = cycle_path


class HealingBudgetExceededError(HealerError):
    """
    Raised when the healing budget is exceeded.

    Prevents infinite loops and excessive resource consumption
    during autonomous healing operations.
    """

    def __init__(self, budget_used: int, budget_limit: int):
        message = f"Healing budget exceeded: {budget_used} > {budget_limit}"
        super().__init__(message, {"budget_used": budget_used, "budget_limit": budget_limit})
        self.budget_used = budget_used
        self.budget_limit = budget_limit


class ValidationRegistryError(HealerError):
    """
    Raised when there's an error in the validation registry lookup.

    This occurs when the CANON_VALIDATION_REGISTRY is malformed
    or contains invalid validation rules.
    """

    def __init__(self, registry_key: str, reason: str):
        message = f"Validation registry error for '{registry_key}': {reason}"
        super().__init__(message, {"registry_key": registry_key, "reason": reason})
        self.registry_key = registry_key
        self.reason = reason


class HealingTimeoutError(HealerError):
    """
    Raised when a healing operation times out.

    Used to prevent hanging healing operations that might
    be stuck in infinite loops or waiting on external resources.
    """

    def __init__(self, timeout_seconds: int, operation: str):
        message = f"Healing operation '{operation}' timed out after {timeout_seconds} seconds"
        super().__init__(message, {"timeout_seconds": timeout_seconds, "operation": operation})
        self.timeout_seconds = timeout_seconds
        self.operation = operation


class SovereignError(HealerError):
    """
    Raised when a sovereign operation is violated.

    This occurs when architectural sovereignty rules are broken
    or when unauthorized changes are attempted.
    """

    def __init__(self, message: str, violation_type: str | None = None):
        super().__init__(message)
        self.violation_type = violation_type


class ConfigurationError(HealerError):
    """
    Raised when there's a configuration error.

    This occurs when the system configuration is invalid
    or missing required parameters.
    """

    def __init__(self, message: str, config_key: str | None = None):
        super().__init__(message)
        self.config_key = config_key
