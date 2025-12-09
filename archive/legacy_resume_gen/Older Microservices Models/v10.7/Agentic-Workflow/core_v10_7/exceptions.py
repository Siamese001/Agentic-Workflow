"""Exception hierarchy for the core v10.7 workflow runtime."""
from __future__ import annotations

from asyncio import TimeoutError as AsyncTimeoutError


class WorkflowError(Exception):
    """Base exception for workflow failures."""


class ModelAPIError(WorkflowError):
    """Raised when an LLM provider call fails."""


class JSONParsingError(WorkflowError):
    """Raised when JSON parsing fails."""


class ValidationError(WorkflowError):
    """Raised when workflow validation fails."""


class FileIOError(WorkflowError):
    """Raised when file IO fails."""


class CostCeilingExceededError(WorkflowError):
    """Raised when a workflow exceeds the configured cost ceiling."""


class CircuitBreakerOpenError(WorkflowError):
    """Raised when the circuit breaker remains open."""


class PydanticSchemaError(ValidationError):
    """Raised when Pydantic validation fails."""


class WorkflowTimeoutError(WorkflowError, AsyncTimeoutError):
    """Raised when async workflow execution exceeds its timeout."""


class MCPClientInitializationError(WorkflowError):
    """Raised when an MCP client fails to initialize."""


__all__ = [
    "WorkflowError",
    "ModelAPIError",
    "JSONParsingError",
    "ValidationError",
    "FileIOError",
    "CostCeilingExceededError",
    "CircuitBreakerOpenError",
    "PydanticSchemaError",
    "WorkflowTimeoutError",
    "MCPClientInitializationError",
]
