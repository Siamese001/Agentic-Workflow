"""Dataclass models for tool_perform_observability_operation."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from .tool_perform_observability_operation_enums import *

@dataclass
class ToolOperationDefinition:
    """Definition of a tool operation."""
    operation_id: str
    tool_name: str
    operation_type: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    scope: OperationScope
    timeout: float = 30.0
    retry_policy: Dict[str, Any] = field(default_factory=dict)

@dataclass
class OperationExecutionContext:
    """Context for operation execution."""
    execution_id: str
    operation_id: str
    mode: OperationMode
    caller_context: Optional[Dict[str, Any]] = None
    trace_context: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class OperationExecutionConfig:
    """Configuration for operation execution."""
    default_timeout: float = 30.0
    enable_tracing: bool = True
    enable_metrics: bool = True
    enable_validation: bool = True
    max_concurrent_operations: int = 100

@dataclass
class OperationExecutionResult:
    """Result of operation execution."""
    execution_id: str
    operation_id: str
    success: bool
    output: Optional[Any] = None
    metrics: Dict[str, float] = field(default_factory=dict)
    traces: List[Dict[str, Any]] = field(default_factory=list)
    artifacts: List[str] = field(default_factory=list)
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    execution_time: float = 0.0
