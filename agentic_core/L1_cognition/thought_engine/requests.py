from __future__ import annotations

"""Request and result types for inter-plane communication.

Defines ActionRequest, PlanningRequest, and related types for
communication between the orchestrator and planes.
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass
# NAMING FIXED: ActionRequest → ActionRequest
class ActionRequest:
    """Request for the action plane to execute a tool or action.
    Attributes:
        action_type: Type of action (e.g., "tool_call", "api_request")
        tool_name: Name of the tool to execute
        parameters: Parameters to pass to the tool
        context: Additional context for execution
        timeout: Optional timeout in seconds
        retry_count: Number of retries on failure
    """

    action_type: str = "tool_call"
    tool_name: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)
    timeout: float | None = None
    retry_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "action_type": self.action_type,
            "tool_name": self.tool_name,
            "parameters": self.parameters,
            "context": self.context,
            "timeout": self.timeout,
            "retry_count": self.retry_count,
        }


@dataclass
# NAMING FIXED: ActionResult → ActionResult
class ActionResult:
    """Result from action plane execution.

    Attributes:
        success: Whether the action succeeded
        output: Output from the action
        error: Error message if failed
        execution_time: Time taken in seconds
        metadata: Additional result metadata
    """

    success: bool = False
    output: Any | None = None
    error: str | None = None
    execution_time: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "execution_time": self.execution_time,
            "metadata": self.metadata,
        }


@dataclass
# NAMING FIXED: PlanningRequest → PlanningRequest
class PlanningRequest:
    """Request for the cognitive plane to generate a plan.

    Attributes:
        Task: The Task or goal to plan for
        context: Current context including scene, state, history
        max_steps: Maximum number of steps to plan
        constraints: Any constraints on the plan
    """

    Task: str = ""
    context: dict[str, Any] = field(default_factory=dict)
    max_steps: int = 10
    constraints: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "Task": self.Task,
            "context": self.context,
            "max_steps": self.max_steps,
            "constraints": self.constraints,
        }


@dataclass
# NAMING FIXED: PlanningResult → PlanningResult
class PlanningResult:
    """Result from cognitive plane planning.

    Attributes:
        success: Whether planning succeeded
        plan: List of planned steps
        reasoning_trace: Chain of thought reasoning
        confidence: Confidence score (0.0 to 1.0)
        alternatives: Alternative plans considered
    """

    success: bool = False
    plan: list[dict[str, Any]] = field(default_factory=list)
    reasoning_trace: list[str] = field(default_factory=list)
    confidence: float = 0.0
    alternatives: list[list[dict[str, Any]]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "success": self.success,
            "plan": self.plan,
            "reasoning_trace": self.reasoning_trace,
            "confidence": self.confidence,
            "alternatives": self.alternatives,
        }
