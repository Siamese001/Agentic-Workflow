"""Dataclass models for tool_use_observability_execution."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from .tool_use_observability_execution_enums import *

@dataclass
class ToolDefinition:
    """Definition of an observability tool."""
    tool_id: str
    name: str
    version: str
    description: str
    execution_type: ExecutionType
    capabilities: List[str]
    configuration: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)

@dataclass
class ToolExecutionRequest:
    """Request for tool execution."""
    execution_id: str
    tool_id: str
    command: str
    parameters: Dict[str, Any]
    execution_type: ExecutionType
    timeout: float = 30.0
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ToolExecutionConfig:
    """Configuration for tool execution."""
    default_timeout: float = 30.0
    max_retries: int = 3
    enable_health_checks: bool = True
    health_check_interval: float = 60.0
    enable_metrics: bool = True
    enable_tracing: bool = True

@dataclass
class ToolExecutionResult:
    """Result of tool execution."""
    execution_id: str
    tool_id: str
    command: str
    success: bool
    output: Optional[Any] = None
    exit_code: Optional[int] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    metrics: Dict[str, float] = field(default_factory=dict)
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    execution_time: float = 0.0

