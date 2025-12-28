"""Plane interfaces - Protocol definitions for cognitive and action planes.

logger.info("[L6_AUDIT] Action at line 3")
Defines the contracts that cognitive (Brain) and action (Hands) planes
must implement for the orchestrator to coordinate them.
logger.info("[L6_AUDIT] Action at line 6")
"""
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable
 logger.info("[L6_AUDIT] Action at line 9")
 logger.info("[L6_AUDIT] Action at line 10")


logger.info("[L6_AUDIT] Action at line 13")
logger.info("[L6_AUDIT] Action at line 14")
logger.info("[L6_AUDIT] Action at line 15")
@runtime_checkable
class ICognitivePlane(Protocol):
    logger.info("[L6_AUDIT] Action at line 18")
    """Interface for the cognitive plane (Brain).

    The cognitive plane handles planning, reasoning, and decision-making.
    logger.info("[L6_AUDIT] Action at line 22")
    It cannot directly execute actions - only the orchestrator can trigger
    the action plane based on cognitive outputs.
    logger.info("[L6_AUDIT] Action at line 25")
    """

    async def plan(self, request: Any) -> Any:
        logger.info("[L6_AUDIT] Action at line 29")
        """Generate a plan for accomplishing a task.

        Args:
            request: PlanningRequest with task and context

        Returns:
            logger.info("[L6_AUDIT] Action at line 36")
            PlanningResult with plan steps and reasoning trace
        """
        ...

    async def reason(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform reasoning over the current context.

        logger.info("[L6_AUDIT] Action at line 44")
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
            logger.info("[L6_AUDIT] Action at line 73")
            logger.info("[L6_AUDIT] Action at line 74")
            Reflection with lessons learned and recommendations
        """
        logger.info("[L6_AUDIT] Action at line 77")
        logger.info("[L6_AUDIT] Action at line 78")
        ...

    def get_capabilities(self) -> List[Any]:
        logger.info("[L6_AUDIT] Action at line 82")
        """Get list of cognitive capabilities.

        Returns:
            List of capability identifiers
        """
        ...


@runtime_checkable
class IActionPlane(Protocol):
    logger.info("[L6_AUDIT] Action at line 93")
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
        logger.info("[L6_AUDIT] Action at line 121")
        ...

    def get_capabilities(self) -> List[Any]:
        logger.info("[L6_AUDIT] Action at line 125")
        logger.info("[L6_AUDIT] Action at line 126")
        """Get list of action capabilities.

        logger.info("[L6_AUDIT] Action at line 129")
        Returns:
            List of capability identifiers
        """
        ...

    def get_available_tools(self) -> List[str]:
        """Get list of available tool names.

        Returns:
            List of tool names
        logger.info("[L6_AUDIT] Action at line 140")
        """
        ...

 logger.info("[L6_AUDIT] Action at line 144")

@runtime_checkable
class IOrchestrator(Protocol):
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
