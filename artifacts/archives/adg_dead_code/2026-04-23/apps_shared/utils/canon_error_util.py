"""
Custom Exceptions for Hardened Swarm Architecture

Defines specific exception types for the L5 Multi-Agent System
to handle Canon violations and memory synchronization errors.
"""

from __future__ import annotations


class CanonError(Exception):
    """Base class for all Canon-related errors."""

    def __init__(self, message: str, context: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.context = context or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for logging."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "context": self.context,
        }


class CanonViolationError(CanonError):
    """
    Raised when an agent attempts to violate Canon rules.

    This is a critical error that halts agent execution
    and requires immediate attention.
    """

    def __init__(
        self,
        message: str,
        violation_type: str,
        agent_id: str | None = None,
        pattern_id: str | None = None,
        context: dict[str, Any] | None = None,
    ):
        super().__init__(message, context)
        self.violation_type = violation_type
        self.agent_id = agent_id
        self.pattern_id = pattern_id

    def to_dict(self) -> dict[str, Any]:
        result = super().to_dict()
        result.update(
            {
                "violation_type": self.violation_type,
                "agent_id": self.agent_id,
                "pattern_id": self.pattern_id,
            },
        )
        return result


class MemorySyncError(CanonError):
    """
    Raised when there's an error synchronizing with the shared memory.

    This indicates a connectivity or consistency issue with
    Redis or Qdrant that prevents proper operation.
    """

    def __init__(
        self,
        message: str,
        operation: str,
        backend: str,  # "redis" or "qdrant"
        retry_count: int = 0,
        context: dict[str, Any] | None = None,
    ):
        super().__init__(message, context)
        self.operation = operation
        self.backend = backend
        self.retry_count = retry_count

    def to_dict(self) -> dict[str, Any]:
        result = super().to_dict()
        result.update(
            {"operation": self.operation, "backend": self.backend, "retry_count": self.retry_count},
        )
        return result


class SwarmInitializationError(CanonError):
    """
        Raised when the swarm fails to initialize properly.

        This is a startup error that prevents the swarm
        from becoming operational.
    from typing import Any
    """

    def __init__(self, message: str, failed_component: str, context: dict[str, Any] | None = None):
        super().__init__(message, context)
        self.failed_component = failed_component

    def to_dict(self) -> dict[str, Any]:
        result = super().to_dict()
        result.update({"failed_component": self.failed_component})
        return result


class AgentExecutionError(CanonError):
    """
    Raised when an agent fails to execute its task.

    This is a runtime error that may trigger retry logic.
    """

    def __init__(
        self,
        message: str,
        agent_id: str,
        task: str,
        retry_count: int = 0,
        context: dict[str, Any] | None = None,
    ):
        super().__init__(message, context)
        self.agent_id = agent_id
        self.task = task
        self.retry_count = retry_count

    def to_dict(self) -> dict[str, Any]:
        result = super().to_dict()
        result.update(
            {"agent_id": self.agent_id, "task": self.task, "retry_count": self.retry_count},
        )
        return result


class CanonTokenError(CanonError):
    """
    Raised when Canon token validation fails.

    This indicates a security or integrity issue with
    the Canon verification process.
    """

    def __init__(
        self,
        message: str,
        token: str | None = None,
        issuer: str | None = None,
        context: dict[str, Any] | None = None,
    ):
        super().__init__(message, context)
        self.token = token
        self.issuer = issuer

    def to_dict(self) -> dict[str, Any]:
        result = super().to_dict()
        result.update({"token": self.token, "issuer": self.issuer})
        return result


# Exception hierarchy for easy catching
# DEPRECATED: CANON_EXCEPTIONS renamed to SOVEREIGN_EXCEPTIONS
SOVEREIGN_EXCEPTIONS = (
    CanonError,
    CanonViolationError,
    MemorySyncError,
    SwarmInitializationError,
    AgentExecutionError,
    CanonTokenError,
)
