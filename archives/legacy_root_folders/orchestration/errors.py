"""
Orchestration layer error definitions.

This module provides error classes specific to orchestration operations,
moved from core/errors.py during canonical structure cleanup.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional
from dataclasses import dataclass


class ErrorSeverity(str, Enum):
    """Severity levels for workflow errors."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class WorkflowErrorCode(str, Enum):
    """Standard error codes for workflow operations."""
    NODE_EXECUTION_FAILED = "node_execution_failed"
    SAFETY_VIOLATION = "safety_violation"
    STATE_TRANSITION_FAILED = "state_transition_failed"
    TIMEOUT = "timeout"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    VALIDATION_FAILED = "validation_failed"
    DEPENDENCY_FAILED = "dependency_failed"
    CONFIGURATION_ERROR = "configuration_error"


@dataclass
class ErrorContext:
    """Context information for workflow errors."""
    node_id: Optional[str] = None
    workflow_id: Optional[str] = None
    execution_id: Optional[str] = None
    timestamp: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None


class WorkflowError(Exception):
    """Base class for all workflow-related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[WorkflowErrorCode] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[ErrorContext] = None,
    ):
        super().__init__(message)
        self.error_code = error_code
        self.severity = severity
        self.context = context or ErrorContext()


class NodeExecutionError(WorkflowError):
    """Raised when a node execution fails."""
    
    def __init__(
        self,
        message: str,
        node_id: str,
        context: Optional[ErrorContext] = None,
    ):
        super().__init__(
            message,
            error_code=WorkflowErrorCode.NODE_EXECUTION_FAILED,
            context=context,
        )
        self.node_id = node_id


class SafetyViolationError(WorkflowError):
    """Raised when safety validation fails."""
    
    def __init__(
        self,
        message: str,
        violation_type: str,
        context: Optional[ErrorContext] = None,
    ):
        super().__init__(
            message,
            error_code=WorkflowErrorCode.SAFETY_VIOLATION,
            severity=ErrorSeverity.HIGH,
            context=context,
        )
        self.violation_type = violation_type


class StateTransitionError(WorkflowError):
    """Raised when state transition fails."""
    
    def __init__(
        self,
        message: str,
        from_state: str,
        to_state: str,
        context: Optional[ErrorContext] = None,
    ):
        super().__init__(
            message,
            error_code=WorkflowErrorCode.STATE_TRANSITION_FAILED,
            context=context,
        )
        self.from_state = from_state
        self.to_state = to_state
