"""
03_runtime/shared/exceptions.py
AUTO-HARDENED BY ZERO-LOSS MERGE ENGINE
L5 CANONICAL — WINDSURF Ω — 2025-12-07
MERKLE-INTENDED: ca2f37be3f2bdc98bace3f3d1c9562fd1f315b85c62299f119c7e71df3f3354e
"""


from __future__ import annotations

from typing import Any, Dict, List, Optional


class AgenticWorkflowError(Exception):
    """
    Base exception for all Agentic Workflow errors.

    All custom exceptions in the system should inherit from this class
    to enable consistent error handling and logging.

    Attributes:
        message: Human-readable error description
        error_code: Machine-readable error code for programmatic handling
        context: Additional context about the error
        recoverable: Whether the error is potentially recoverable
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        recoverable: bool = False,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
        self.recoverable = recoverable

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/serialization."""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context,
            "recoverable": self.recoverable,
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r}, error_code={self.error_code!r})"


# =============================================================================
# EXECUTION ERRORS
# =============================================================================

class HopExecutionError(AgenticWorkflowError):
    """
    Raised when a workflow hop fails to execute successfully.

    A hop is a discrete step in the workflow pipeline. This error indicates
    that a specific hop encountered an unrecoverable failure.

    Attributes:
        hop_id: Identifier of the failed hop
        hop_name: Human-readable name of the hop
        phase: The phase in which the hop failed
    """

    def __init__(
        self,
        message: str,
        hop_id: Optional[str] = None,
        hop_name: Optional[str] = None,
        phase: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        context = kwargs.pop("context", {})
        context.update({
            "hop_id": hop_id,
            "hop_name": hop_name,
            "phase": phase,
        })
        super().__init__(message, context=context, **kwargs)
        self.hop_id = hop_id
        self.hop_name = hop_name
        self.phase = phase


class StagingBufferError(AgenticWorkflowError):
    """
    Raised when the staging buffer encounters data integrity issues.

    The staging buffer is an immutable data structure used to pass data
    between workflow phases. This error indicates an attempt to violate
    its immutability guarantees.
    """

    def __init__(
        self,
        message: str,
        key: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        context = kwargs.pop("context", {})
        context.update({
            "key": key,
            "operation": operation,
        })
        super().__init__(message, context=context, **kwargs)
        self.key = key
        self.operation = operation


class CircuitBreakerOpenError(AgenticWorkflowError):
    """
    Raised when a circuit breaker is open and rejects requests.

    Circuit breakers protect the system from cascading failures by
    temporarily blocking requests to failing services.

    Attributes:
        service_name: Name of the protected service
        failure_count: Number of failures that triggered the breaker
        reset_time: Estimated time until the breaker resets
    """

    def __init__(
        self,
        message: str,
        service_name: Optional[str] = None,
        failure_count: int = 0,
        reset_time: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        context = kwargs.pop("context", {})
        context.update({
            "service_name": service_name,
            "failure_count": failure_count,
            "reset_time": reset_time,
        })
        super().__init__(message, context=context, recoverable=True, **kwargs)
        self.service_name = service_name
        self.failure_count = failure_count
        self.reset_time = reset_time


class PhaseTimeoutError(AgenticWorkflowError):
    """
    Raised when a RAG phase execution exceeds its timeout.

    Attributes:
        phase_name: Name of the timed-out phase
        timeout_seconds: The timeout threshold that was exceeded
        elapsed_seconds: Actual elapsed time before timeout
    """

    def __init__(
        self,
        message: str,
        phase_name: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        elapsed_seconds: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        context = kwargs.pop("context", {})
        context.update({
            "phase_name": phase_name,
            "timeout_seconds": timeout_seconds,
            "elapsed_seconds": elapsed_seconds,
        })
        super().__init__(message, context=context, recoverable=True, **kwargs)
        self.phase_name = phase_name
        self.timeout_seconds = timeout_seconds
        self.elapsed_seconds = elapsed_seconds


class PipelineError(AgenticWorkflowError):
    """
    Raised when a pipeline operation fails.

    Pipelines are sequences of operations that transform data.
    This error indicates a failure in pipeline execution.
    """

    def __init__(
        self,
        message: str,
        pipeline_name: Optional[str] = None,
        stage: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        context = kwargs.pop("context", {})
        context.update({
            "pipeline_name": pipeline_name,
            "stage": stage,
        })
        super().__init__(message, context=context, **kwargs)
        self.pipeline_name = pipeline_name
        self.stage = stage


# =============================================================================
# VALIDATION ERRORS
# =============================================================================

class FactualFailureException(AgenticWorkflowError):
    """
    Raised when a high-signal factual or strategic check fails.

    This exception triggers a Slow Loop for more thorough validation
    and potential correction of factual errors.

    Attributes:
        check_name: Name of the failed check
        expected: Expected value or condition
        actual: Actual value or condition found
    """

    def __init__(
        self,
        message: str,
        check_name: Optional[str] = None,
        expected: Optional[Any] = None,
        actual: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        context = kwargs.pop("context", {})
        context.update({
            "check_name": check_name,
            "expected": str(expected) if expected is not None else None,
            "actual": str(actual) if actual is not None else None,
        })
        super().__init__(message, context=context, recoverable=True, **kwargs)
        self.check_name = check_name
        self.expected = expected
        self.actual = actual


class ValidationError(AgenticWorkflowError):
    """
    Raised when data validation fails.

    Attributes:
        field: The field that failed validation
        rule: The validation rule that was violated
        violations: List of all validation violations
    """

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        rule: Optional[str] = None,
        violations: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        context = kwargs.pop("context", {})
        context.update({
            "field": field,
            "rule": rule,
            "violations": violations or [],
        })
        super().__init__(message, context=context, **kwargs)
        self.field = field
        self.rule = rule
        self.violations = violations or []


# =============================================================================
# CONFIGURATION ERRORS
# =============================================================================

class ConfigurationError(AgenticWorkflowError):
    """
    Raised when configuration is invalid or missing.

    Attributes:
        config_key: The configuration key that is problematic
        config_file: The configuration file, if applicable
    """

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        config_file: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        context = kwargs.pop("context", {})
        context.update({
            "config_key": config_key,
            "config_file": config_file,
        })
        super().__init__(message, context=context, **kwargs)
        self.config_key = config_key
        self.config_file = config_file


# =============================================================================
# API ERRORS
# =============================================================================

class APIError(AgenticWorkflowError):
    """
    Raised when an external API call fails.

    Attributes:
        api_name: Name of the API that failed
        status_code: HTTP status code, if applicable
        response_body: Response body, if available
        retry_after: Suggested retry delay in seconds
    """

    def __init__(
        self,
        message: str,
        api_name: Optional[str] = None,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
        retry_after: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        context = kwargs.pop("context", {})
        context.update({
            "api_name": api_name,
            "status_code": status_code,
            "response_body": response_body[:500] if response_body else None,
            "retry_after": retry_after,
        })
        recoverable = status_code in (429, 500, 502, 503, 504) if status_code else False
        super().__init__(message, context=context, recoverable=recoverable, **kwargs)
        self.api_name = api_name
        self.status_code = status_code
        self.response_body = response_body
        self.retry_after = retry_after


class MCPClientInitializationError(AgenticWorkflowError):
    """
    Raised when an MCP client fails to initialize.

    MCP (Model Context Protocol) clients provide access to external
    services like Redis, ChromaDB, etc.

    Attributes:
        client_name: Name of the MCP client
        service_type: Type of service (redis, chromadb, etc.)
    """

    def __init__(
        self,
        message: str,
        client_name: Optional[str] = None,
        service_type: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        context = kwargs.pop("context", {})
        context.update({
            "client_name": client_name,
            "service_type": service_type,
        })
        super().__init__(message, context=context, recoverable=True, **kwargs)
        self.client_name = client_name
        self.service_type = service_type


# =============================================================================
# CACHE ERRORS
# =============================================================================

class SemanticCacheError(AgenticWorkflowError):
    """
    Raised when semantic cache operations fail.

    The semantic cache stores embeddings and semantic representations
    for efficient retrieval and comparison.

    Attributes:
        cache_key: The cache key involved
        operation: The operation that failed (get, set, invalidate)
    """

    def __init__(
        self,
        message: str,
        cache_key: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        context = kwargs.pop("context", {})
        context.update({
            "cache_key": cache_key,
            "operation": operation,
        })
        super().__init__(message, context=context, recoverable=True, **kwargs)
        self.cache_key = cache_key
        self.operation = operation


# =============================================================================
# EXCEPTION UTILITIES
# =============================================================================

def is_recoverable(exc: Exception) -> bool:
    """
    Check if an exception is potentially recoverable.

    Args:
        exc: The exception to check

    Returns:
        True if the exception is recoverable, False otherwise
    """
    if isinstance(exc, AgenticWorkflowError):
        return exc.recoverable

    # Standard library exceptions that are typically recoverable
    recoverable_types = (
        TimeoutError,
        ConnectionError,
        ConnectionResetError,
        ConnectionRefusedError,
    )
    return isinstance(exc, recoverable_types)


def get_error_chain(exc: Exception) -> List[Exception]:
    """
    Get the chain of exceptions (including __cause__ and __context__).

    Args:
        exc: The exception to trace

    Returns:
        List of exceptions in the chain, from innermost to outermost
    """
    chain = [exc]
    current = exc

    while current.__cause__ is not None:
        chain.append(current.__cause__)
        current = current.__cause__

    return chain
