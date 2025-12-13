"""Dataclass models for invoke_observability_tool."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
# from .invoke_observability_tool_enums import *  # Star import removed

@dataclass
class ToolEndpoint:
    """Definition of a tool endpoint."""
    endpoint_id: str
    url: str
    protocol: str
    authentication: Optional[Dict[str, Any]] = None
    headers: Dict[str, str] = field(default_factory=dict)
    timeout: float = 30.0

@dataclass
class InvocationRequest:
    """Request for tool invocation."""
    invocation_id: str
    tool_name: str
    method: str
    parameters: Dict[str, Any]
    endpoint: Optional[ToolEndpoint] = None
    invocation_type: InvocationType = InvocationType.DIRECT
    response_format: ResponseFormat = ResponseFormat.JSON
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class InvocationConfig:
    """Configuration for tool invocation."""
    default_timeout: float = 30.0
    retry_attempts: int = 3
    enable_caching: bool = True
    cache_ttl: float = 300.0
    enable_compression: bool = False

@dataclass
class InvocationResponse:
    """Response from tool invocation."""
    invocation_id: str
    tool_name: str
    success: bool
    data: Optional[Any] = None
    headers: Dict[str, str] = field(default_factory=dict)
    status_code: Optional[int] = None
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    execution_time: float = 0.0
