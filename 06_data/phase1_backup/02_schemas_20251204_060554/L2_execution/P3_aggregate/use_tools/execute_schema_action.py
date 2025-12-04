"""
Schema definitions for schema action execution and operation.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class ActionType(Enum):
    """Types of schema actions."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    VALIDATE = "validate"
    TRANSFORM = "transform"


class ExecutionMode(Enum):
    """Action execution modes."""
    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"
    BATCH = "batch"
    STREAMING = "streaming"


@dataclass
class ActionParameters:
    """Schema for action execution parameters."""
    action_type: ActionType
    execution_mode: ExecutionMode
    target_schema_id: str
    parameters: Dict[str, Any]
    timeout_seconds: int = 300


@dataclass
class ActionContext:
    """Schema for action execution context."""
    context_id: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    environment: str = "production"
    metadata: Optional[Dict[str, str]] = None


@dataclass
class ActionExecutionResult:
    execution_id: str
    action_type: ActionType
    status: str
    execution_time_ms: int
    result_data: Optional[Dict[str, Any]] = None
    error_details: Optional[str] = None
    """Schema for action execution results."""