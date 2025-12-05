from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ToolCallRequest(BaseModel):
    """Structured request for executing a tool inside the sandbox.

    This model is intentionally generic and does not depend on any
    particular tool implementation.
    """

    tool_name: str
    args: List[str] = Field(default_factory=list)
    env: Dict[str, str] = Field(default_factory=dict)
    timeout_s: float = 30.0
    resource_limits: Dict[str, Any] = Field(default_factory=dict)


class ToolCallResult(BaseModel):
    """Result of running a tool inside the sandbox microVM."""

    success: bool
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    resource_usage: Dict[str, Any] = Field(default_factory=dict)
    duration_ms: int = 0


class SandboxEvent(BaseModel):
    """Typed event emitted for sandbox observability hooks."""

    name: str
    ts_ms: int
    vm_id: Optional[str] = None
    tool_name: Optional[str] = None
    attributes: Dict[str, Any] = Field(default_factory=dict)



