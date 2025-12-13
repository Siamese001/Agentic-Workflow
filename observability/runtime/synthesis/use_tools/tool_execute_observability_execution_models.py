"""Dataclass models for tool_execute_observability_execution."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
# from .tool_execute_observability_execution_enums import *  # Star import removed

@dataclass
class ToolDefinition:
    """Definition of an observability tool."""
    tool_id: str
    tool_type: ToolType
    name: str
    version: str
    description: str
    parameters: Dict[str, Dict[str, Any]]
    capabilities: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)

@dataclass
class ToolExecutionContext:
    """Context for tool execution."""
    execution_id: str
    tool_id: str
    mode: ExecutionMode
    caller_id: Optional[str] = None
    session_id: Optional[str] = None
    trace_context: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ToolExecutionConfig:
    """Configuration for tool execution."""
    timeout: float = 30.0
    retry_count: int = 3
    enable_tracing: bool = True
    enable_metrics: bool = True
    buffer_size: int = 1000

@dataclass
class ToolExecutionResult:
    """Result of tool execution."""
    execution_id: str
    tool_id: str
    success: bool
    output: Optional[Any] = None
    metrics: Dict[str, float] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    execution_time: float = 0.0
