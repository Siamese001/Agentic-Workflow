from __future__ import annotations


class AgenticWorkflowError(Exception):
    """Base exception for agentic workflow."""


class HopExecutionError(AgenticWorkflowError):
    """Error in hop execution."""


class ValidationError(AgenticWorkflowError):
    """Validation error."""


class ApiError(AgenticWorkflowError):
    """API-related error."""


class CircuitBreakerOpenError(AgenticWorkflowError):
    """Circuit breaker is open."""


__all__ = [
    "AgenticWorkflowError",
    "HopExecutionError",
    "ValidationError",
    "ApiError",
    "CircuitBreakerOpenError",
]
