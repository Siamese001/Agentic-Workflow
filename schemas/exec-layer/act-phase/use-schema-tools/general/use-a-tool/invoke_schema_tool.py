"""
Schema definitions for schema tool invocation and execution.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class ToolType(Enum):
    """Schema tool invocation types."""
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"
    ANALYSIS = "analysis"
    GENERATION = "generation"


class InvocationMode(Enum):
    """Tool invocation modes."""
    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"
    STREAMING = "streaming"
    BATCH = "batch"


@dataclass
class ToolInvocation:
    """Schema for individual tool invocation."""
    invocation_id: str
    tool_type: ToolType
    tool_name: str
    parameters: Dict[str, Any]
    invocation_mode: InvocationMode
    timeout_ms: int = 30000


@dataclass
class ToolExecutionContext:
    """Schema for tool execution context."""
    context_id: str
    target_schema_id: str
    invocations: List[ToolInvocation]
    execution_environment: Dict[str, Any]
    execution_timestamp: str


@dataclass
class ToolInvocationResult:
    """Schema for tool invocation results."""
    result_id: str
    context: ToolExecutionContext
    execution_successful: bool
    outputs: List[Dict[str, Any]]
    execution_time_ms: int