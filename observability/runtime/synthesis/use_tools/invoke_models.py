"""Dataclass models for tool_invoke_observability_tool."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from .tool_invoke_observability_tool_enums import *

@dataclass
class ToolSpecification:
    """Specification of an observability tool."""
    tool_id: str
    name: str
    version: str
    category: ToolCategory
    protocol: ToolProtocol
    endpoint: str
    methods: List[str]
    parameters_schema: Dict[str, Dict[str, Any]]
    authentication: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ToolInvocationContext:
    """Context for tool invocation."""
    invocation_id: str
    tool_id: str
    method: str
    caller_id: Optional[str] = None
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None
    timeout: float = 30.0
    retry_policy: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ToolInvocationConfig:
    """Configuration for tool invocation."""
    default_timeout: float = 30.0
    max_retries: int = 3
    enable_circuit_breaker: bool = True
    circuit_breaker_threshold: int = 5
    enable_metrics: bool = True
    enable_tracing: bool = True

@dataclass
class ToolInvocationResult:
    """Result of tool invocation."""
    invocation_id: str
    tool_id: str
    method: str
    success: bool
    response: Optional[Any] = None
    response_code: Optional[int] = None
    headers: Dict[str, str] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    execution_time: float = 0.0
