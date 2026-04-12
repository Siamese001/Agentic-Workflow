"""
Runtime Exceptions for Agentic Workflow

This module defines structured exception classes for proper error propagation
in the agent runtime, preventing "Silent Swallower" anti-patterns.

Phase 2 Landmine Remediation - Critical Risk Mitigation
"""

from typing import Any


class AgentRuntimeError(Exception):
    """Base exception for all agent runtime errors."""

    def __init__(self, message: str, context: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.context = context or {}

    def __str__(self) -> str:
        if self.context:
            return f"{self.message} | Context: {self.context}"
        return self.message


class ToolExecutionError(AgentRuntimeError):
    """
    Raised when a tool execution fails.

    This exception replaces silent error swallowing in tool execution,
    ensuring agents are aware of tool failures and can take corrective action.
    """

    def __init__(
        self,
        tool_name: str,
        message: str,
        original_error: Exception | None = None,
        tool_args: dict[str, Any] | None = None,
    ):
        context = {
            "tool_name": tool_name,
            "tool_args": tool_args or {},
            "original_error_type": type(original_error).__name__ if original_error else None,
        }
        super().__init__(message, context)
        self.tool_name = tool_name
        self.original_error = original_error
        self.tool_args = tool_args or {}


class ToolNotFoundError(AgentRuntimeError):
    """Raised when a requested tool is not found in the registry."""

    def __init__(self, tool_name: str, available_tools: list[str] | None = None):
        message = f"Tool '{tool_name}' not found in registry"
        context = {"tool_name": tool_name, "available_tools": available_tools or []}
        super().__init__(message, context)
        self.tool_name = tool_name
        self.available_tools = available_tools or []


class HealExecutionError(AgentRuntimeError):
    """
    Raised when a heal operation fails.

    This exception replaces silent error returns in @standard_heal decorator,
    ensuring heal failures are properly propagated for debugging.
    """

    def __init__(
        self,
        agent_name: str,
        method_name: str,
        message: str,
        original_error: Exception | None = None,
    ):
        context = {
            "agent_name": agent_name,
            "method_name": method_name,
            "original_error_type": type(original_error).__name__ if original_error else None,
        }
        super().__init__(message, context)
        self.agent_name = agent_name
        self.method_name = method_name
        self.original_error = original_error


class PatternExecutionError(AgentRuntimeError):
    """Raised when a reasoning pattern fails to execute."""

    def __init__(self, pattern_name: str, message: str, state_context: dict[str, Any] | None = None):
        context = {"pattern_name": pattern_name, "state_context": state_context or {}}
        super().__init__(message, context)
        self.pattern_name = pattern_name


class MaxTurnsExceededError(AgentRuntimeError):
    """Raised when agent exceeds maximum allowed turns."""

    def __init__(self, max_turns: int, task_id: str):
        message = f"Agent exceeded maximum turns ({max_turns}) for task '{task_id}'"
        context = {"max_turns": max_turns, "task_id": task_id}
        super().__init__(message, context)
        self.max_turns = max_turns
        self.task_id = task_id
