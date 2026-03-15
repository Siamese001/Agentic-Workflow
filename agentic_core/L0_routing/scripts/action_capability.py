from __future__ import annotations

"Action Plane Interface - The Hands.\n\nPhase 2 - Pillar 1: Layering Model\nDefines the contract for all tool execution and external interactions.\nL2 Execution: Side effects allowed, but controlled and observable.\n"
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


class ActionCapability(Enum):
    """Capabilities provided by the action plane."""

    TOOL_EXECUTION = "tool_execution"
    API_CALLS = "api_calls"
    FILE_OPERATIONS = "file_operations"
    DATABASE_OPERATIONS = "database_operations"
    EXTERNAL_SERVICES = "external_services"
    SEARCH = "search"
    RETRIEVAL = "retrieval"


@dataclass
class ActionRequest:
    """Request for action execution."""

    action_type: str
    tool_name: str
    parameters: dict[str, Any] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)
    timeout_ms: int = 30000
    retry_policy: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ActionRequest.to_dict", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ActionRequest.to_dict", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "ActionRequest.to_dict")
        return {
            "action_type": self.action_type,
            "tool_name": self.tool_name,
            "parameters": self.parameters,
            "context": self.context,
            "timeout_ms": self.timeout_ms,
            "retry_policy": self.retry_policy,
        }


@dataclass
class ActionResult:
    """Result from action execution."""

    success: bool
    output: Any = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    execution_time_ms: float = 0.0
    retries: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "metadata": self.metadata,
            "execution_time_ms": self.execution_time_ms,
            "retries": self.retries,
        }


class IActionPlane(ABC):
    """Interface for the Action Plane (Hands).

    The action plane is responsible for:
    - Tool Execution: Running external tools and APIs
    - Side Effects: Performing actions that change state
    - Resource Management: Managing connections and resources
    - Error Handling: Dealing with failures gracefully

    L2 Constraint: Side effects are allowed but must be:
    - Observable (logged/traced)
    - Reversible when possible
    - Protected by resilience middleware
    """

    @abstractmethod
    async def execute(self, request: ActionRequest) -> ActionResult:
        """Execute an action.

        Args:
            request: Action request with tool and parameters

        Returns:
            ActionResult with output or error
        """
        pass

    @abstractmethod
    async def execute_batch(
        self, requests: list[ActionRequest], parallel: bool = False
    ) -> list[ActionResult]:
        """Execute multiple actions.

        Args:
            requests: List of action requests
            parallel: Whether to execute in parallel

        Returns:
            List of action results
        """
        pass

    @abstractmethod
    async def validate_action(self, request: ActionRequest) -> dict[str, Any]:
        """Validate an action before execution.

        Args:
            request: Action request to validate

        Returns:
            Validation result with any warnings
        """
        pass

    @abstractmethod
    def get_available_tools(self) -> list[str]:
        """Get list of available tools.

        Returns:
            List of tool names
        """
        pass

    @abstractmethod
    def get_tool_schema(self, tool_name: str) -> dict[str, Any]:
        """Get schema for a specific tool.

        Args:
            tool_name: Name of the tool

        Returns:
            Tool schema with parameters and types
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> list[ActionCapability]:
        """Get list of supported action capabilities.

        Returns:
            List of capabilities this plane supports
        """
        pass
