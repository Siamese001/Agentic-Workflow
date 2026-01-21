from __future__ import annotations
"""Action Plane Interface - The Hands.

Phase 2 - Pillar 1: Layering Model
Defines the contract for all tool execution and external interactions.
L2 Execution: Side effects allowed, but controlled and observable.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


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
    parameters: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    timeout_ms: int = 30000
    retry_policy: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
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
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time_ms: float = 0.0
    retries: int = 0

    def to_dict(self) -> Dict[str, Any]:
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
        self,
        requests: List[ActionRequest],
        parallel: bool = False,
    ) -> List[ActionResult]:
        """Execute multiple actions.

        Args:
            requests: List of action requests
            parallel: Whether to execute in parallel

        Returns:
            List of action results
        """
        pass

    @abstractmethod
    async def validate_action(
        self,
        request: ActionRequest,
    ) -> Dict[str, Any]:
        """Validate an action before execution.

        Args:
            request: Action request to validate

        Returns:
            Validation result with any warnings
        """
        pass

    @abstractmethod
    def get_available_tools(self) -> List[str]:
        """Get list of available tools.

        Returns:
            List of tool names
        """
        pass

    @abstractmethod
    def get_tool_schema(self, tool_name: str) -> Dict[str, Any]:
        """Get schema for a specific tool.

        Args:
            tool_name: Name of the tool

        Returns:
            Tool schema with parameters and types
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> List[ActionCapability]:
        """Get list of supported action capabilities.

        Returns:
            List of capabilities this plane supports
        """
        pass
