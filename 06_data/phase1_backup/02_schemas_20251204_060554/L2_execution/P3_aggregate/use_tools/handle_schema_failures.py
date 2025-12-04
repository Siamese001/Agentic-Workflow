"""
Schema definitions for schema failure handling and management.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class FailureType(Enum):
    """Types of schema failures."""
    VALIDATION_ERROR = "validation_error"
    NETWORK_FAILURE = "network_failure"
    TIMEOUT_ERROR = "timeout_error"
    AUTHENTICATION_ERROR = "authentication_error"
    SYSTEM_ERROR = "system_error"


class FailureSeverity(Enum):
    """Failure severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FailureAction(Enum):
    """Failure handling actions."""
    RETRY = "retry"
    ESCALATE = "escalate"
    LOG_AND_CONTINUE = "log_and_continue"
    ABORT = "abort"
    FALLBACK = "fallback"


@dataclass
class FailureDetails:
    """Schema for failure occurrence details."""
    failure_id: str
    failure_type: FailureType
    severity: FailureSeverity
    error_message: str
    timestamp: str
    context: Optional[Dict[str, Any]] = None


@dataclass
class FailureHandlingConfig:
    """Schema for failure handling configuration."""
    failure_type: FailureType
    default_action: FailureAction
    max_retries: int = 3
    escalation_threshold: int = 2
    fallback_enabled: bool = True


@dataclass
class FailureHandlingResult:
    """Schema for failure handling results."""
    handling_id: str
    original_failure: FailureDetails
    action_taken: FailureAction
    resolution_status: str
    handling_metadata: Dict[str, Any]