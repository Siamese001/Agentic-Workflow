from __future__ import annotations
"""Plane interfaces - Protocol definitions for cognitive and action planes.

Defines the contracts that cognitive (Brain) and action (Hands) planes
must implement for the orchestrator to coordinate them.
"""
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin


@runtime_checkable
# NAMING FIXED: ICognitivePlane → ICognitivePlane
class ICognitivePlane(Protocol):
    """Interface for the cognitive plane (Brain).

    The cognitive plane handles planning, reasoning, and decision-making.
    It cannot directly execute actions - only the orchestrator can trigger
    the action plane based on cognitive outputs.
    """

    async def plan(self, request: Any) -> Any:
        """Generate a plan for accomplishing a Task.

        Args:
            request: PlanningRequest with Task and context

        Returns:
            PlanningResult with plan steps and reasoning trace
        """
        ...

    async def reason(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform reasoning over the current context.
        Args:
            context: Current execution context

        Returns:
            Reasoning result with conclusions and confidence
        """
        ...

    async def interpret(self, results: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Interpret action results and determine next steps.

        Args:
            results: Results from executed actions
            context: Current execution context

        Returns:
            Interpretation with state updates and mission status
        """
        ...

    async def reflect(self, execution_trace: List[Dict[str, Any]], outcome: Dict[str, Any]) -> Dict[str, Any]:
        """Reflect on execution and generate insights.

        Args:
            execution_trace: Full trace of execution steps
            outcome: Final outcome of execution

        Returns:
            Reflection with lessons learned and recommendations
        """
        ...

    def get_capabilities(self) -> List[Any]:
        """Get list of cognitive capabilities.

        Returns:
            List of capability identifiers
        """
        ...


@runtime_checkable
# NOT_AN_AGENT — protocol interface, not a true agent — excluded from agent discovery
class IActionPlane(Protocol):
    """Interface for the action plane (Hands).

    The action plane handles tool execution and external interactions.
    It cannot make planning decisions - only execute actions requested
    by the orchestrator based on cognitive outputs.
    """

    async def execute(self, request: Any) -> Any:
        """Execute an action request.

        Args:
            request: ActionRequest with tool and parameters

        Returns:
            ActionResult with output and status
        """
        ...

    async def execute_batch(self, requests: List[Any]) -> List[Any]:
        """Execute multiple action requests.

        Args:
            requests: List of ActionRequests

        Returns:
            List of ActionResults
        """
        ...

    def get_capabilities(self) -> List[Any]:
        """Get list of action capabilities.
        Returns:
            List of capability identifiers
        """
        ...

    def get_available_tools(self) -> List[str]:
        """Get list of available tool names.

        Returns:
            List of tool names
        """
        ...

@runtime_checkable
# NOT_AN_AGENT — protocol interface, not a true agent — excluded from agent discovery
class IOrchestratorAgent(SubatomicTestingMixin, HealerMixin, Protocol, MCPHardenedMixin):
    """Interface for the orchestrator (Nervous System).

    The orchestrator coordinates between cognitive and action planes,
    implementing the Think-Act-Observe cycle.
    """

    async def execute(self, context: Any) -> Any:
        """Execute a mission through the Think-Act-Observe cycle.

        Args:
            context: ExecutionContext with mission and scene

        Returns:
            ExecutionResult with output and trace
        """
        ...

    async def execute_step(self, phase: str, context: Any) -> Any:
        """Execute a single step of the mission cycle.

        Args:
            phase: Current execution phase (e.g., 'plan', 'act', 'observe')
            context: ExecutionContext with current state

        Returns:
            Step result with status and updates
        """
        ...
