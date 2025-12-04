"""
Schema definitions for execution-level schema operations.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class ExecutionStatus(Enum):
    """Execution operation status types."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExecutionType(Enum):
    """Types of execution operations."""
    VALIDATE = "validate"
    TRANSFORM = "transform"
    GENERATE = "generate"
    MIGRATE = "migrate"


@dataclass
class ExecutionParameters:
    """Schema for execution operation parameters."""
    execution_type: ExecutionType
    input_schema_id: str
    output_schema_id: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None
    timeout_seconds: int = 300


@dataclass
class ExecutionResult:
    """Schema for execution operation result."""
    execution_id: str
    status: ExecutionStatus
    start_time: str
    end_time: Optional[str] = None
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


@dataclass
class ExecutionRequest:
    """Schema for execution operation request."""
    parameters: ExecutionParameters
    context: Optional[Dict[str, Any]] = None
    callback_url: Optional[str] = None