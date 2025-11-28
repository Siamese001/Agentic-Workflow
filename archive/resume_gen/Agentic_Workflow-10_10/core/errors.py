"""
Error hierarchy and utilities for workflow execution.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Type, TypeVar


T = TypeVar("T")


class ErrorSeverity(str, Enum):
    """Severity levels for workflow errors."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class WorkflowErrorCode(str, Enum):
    """Standard error codes for workflow execution."""

    # General errors
    UNKNOWN_ERROR = "unknown_error"
    VALIDATION_ERROR = "validation_error"
    CONFIGURATION_ERROR = "configuration_error"

    # Node execution errors
    NODE_EXECUTION_FAILED = "node_execution_failed"
    NODE_TIMEOUT = "node_timeout"
    NODE_DEPENDENCY_FAILED = "node_dependency_failed"

    # State management errors
    STATE_TRANSITION_FAILED = "state_transition_failed"
    STATE_ROLLBACK_FAILED = "state_rollback_failed"
    STATE_CORRUPTION = "state_corruption"

    # Safety/policy errors
    SAFETY_VIOLATION = "safety_violation"
    POLICY_VIOLATION = "policy_violation"

    # Resource errors
    RESOURCE_LIMIT_EXCEEDED = "resource_limit_exceeded"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"


@dataclass
class ErrorContext:
    """Contextual information about where an error occurred."""

    workflow_id: str
    node_id: Optional[str] = None
    component: Optional[str] = None
    operation: Optional[str] = None
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for serialization."""

        return {
            "workflow_id": self.workflow_id,
            "node_id": self.node_id,
            "component": self.component,
            "operation": self.operation,
            "metadata": self.metadata or {},
        }


@dataclass
class WorkflowError(Exception):
    """Base class for all workflow-related errors."""

    code: WorkflowErrorCode
    message: str
    severity: ErrorSeverity = ErrorSeverity.ERROR
    context: Optional[ErrorContext] = None
    cause: Optional[Exception] = None

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert the error to a dictionary for serialization."""

        return {
            "code": self.code.value,
            "message": self.message,
            "severity": self.severity.value,
            "context": self.context.to_dict() if self.context else None,
            "cause": str(self.cause) if self.cause else None,
        }


@dataclass
class NodeExecutionError(WorkflowError):
    """Raised when a node fails to execute."""

    def __init__(
        self,
        message: str,
        node_id: str,
        cause: Optional[Exception] = None,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            code=WorkflowErrorCode.NODE_EXECUTION_FAILED,
            message=message,
            severity=severity,
            context=ErrorContext(
                workflow_id="",  # Filled in by the workflow context if needed
                node_id=node_id,
                component="workflow_engine",
                operation="node_execution",
                metadata=metadata or {},
            ),
            cause=cause,
        )


@dataclass
class SafetyViolationError(WorkflowError):
    """Raised when a safety check fails."""

    def __init__(
        self,
        message: str,
        policy_decisions: Dict[str, Any],
        node_id: Optional[str] = None,
        workflow_id: str = "unknown",
    ) -> None:
        super().__init__(
            code=WorkflowErrorCode.SAFETY_VIOLATION,
            message=message,
            severity=ErrorSeverity.ERROR,
            context=ErrorContext(
                workflow_id=workflow_id,
                node_id=node_id,
                component="safety_layer",
                operation="safety_check",
                metadata={"policy_decisions": policy_decisions},
            ),
        )


@dataclass
class StateTransitionError(WorkflowError):
    """Raised when a state transition or rollback fails."""

    def __init__(
        self,
        message: str,
        transition: Any,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(
            code=WorkflowErrorCode.STATE_TRANSITION_FAILED,
            message=message,
            severity=ErrorSeverity.ERROR,
            context=ErrorContext(
                workflow_id=getattr(transition, "workflow_id", "unknown"),
                node_id=getattr(transition, "node_id", None),
                component="state_manager",
                operation="apply_transition",
                metadata={"transition": str(transition)},
            ),
            cause=cause,
        )


def wrap_error(error: Exception, error_type: Type[WorkflowError], **kwargs: Any) -> WorkflowError:
    """Wrap a generic exception in a WorkflowError."""

    if isinstance(error, WorkflowError):
        return error

    return error_type(message=str(error), cause=error, **kwargs)



