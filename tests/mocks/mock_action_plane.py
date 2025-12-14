"""Mock Action Plane for testing.


logger = logging.getLogger(__name__)
Phase 2 - Pillar 1: Layering Model
Simple mock implementation that returns predefined results.
"""

from typing import Any, Dict, List
import logging

    IActionPlane,
    ActionRequest,
    ActionResult,
    ActionCapability,
)

class MockActionPlane(IActionPlane):
    """Mock action plane for testing.

    Returns predefined action results without actually executing tools.
    Useful for testing orchestrator logic without external dependencies.
    """

    def __init__(
        self,
        predefined_results: Dict[str, Any] = None,
        fail_on_tools: List[str] = None,
    ):
            """Initialize mock action plane.

        Args:
            predefined_results: Optional dict of tool_name -> result
            fail_on_tools: Optional list of tool names that should fail
        """
        self.predefined_results = predefined_results or {}
        self.fail_on_tools = fail_on_tools or []
        self.call_history: List[Dict[str, Any]] = []
        self.available_tools = [
            "mock_tool",
            "search",
            "retrieve",
            "execute",
        ]

    async def execute(self, request: ActionRequest) -> ActionResult:
            """Execute a mock action.

        Args:
            request: Action request

        Returns:
            ActionResult with mock output
        """
        self.call_history.append({
            "method": "execute",
            "request": request.to_dict(),
        })

        # Check if this tool should fail
        if request.tool_name in self.fail_on_tools:
            return ActionResult(
                success=False,
                error=f"Mock failure for tool: {request.tool_name}",
                metadata={"mock": True},
            )

        # Check for predefined result
        if request.tool_name in self.predefined_results:
            output = self.predefined_results[request.tool_name]
        else:
            # Default mock output
            output = {
                "result": f"Mock output from {request.tool_name}",
                "parameters": request.parameters,
            }

        return ActionResult(
            success=True,
            output=output,
            metadata={"mock": True},
            execution_time_ms=10.0,
        )

        """Docstring."""
    async def execute_batch(
        self,
        requests: List[ActionRequest],
        parallel: bool = False,
    ) -> List[ActionResult]:
            """Execute multiple mock actions.

        Args:
            requests: List of action requests
            parallel: Whether to execute in parallel (ignored in mock)

        Returns:
            List of action results
        """
        self.call_history.append({
            "method": "execute_batch",
            "count": len(requests),
            "parallel": parallel,
        })

        results = []
        for request in requests:
            result = await self.execute(request)
            results.append(result)

        return results

        """Docstring."""
    async def validate_action(
        self,
        request: ActionRequest,
    ) -> Dict[str, Any]:
            """Validate a mock action.

        Args:
            request: Action request to validate

        Returns:
            Mock validation result
        """
        self.call_history.append({
            "method": "validate_action",
            "tool": request.tool_name,
        })

        is_valid = request.tool_name in self.available_tools

        return {
            "valid": is_valid,
            "warnings": [] if is_valid else [f"Unknown tool: {request.tool_name}"],
            "mock": True,
        }

    def get_available_tools(self) -> List[str]:
            """Get list of mock tools.

        Returns:
            List of available tool names
        """
        return self.available_tools.copy()

    def get_tool_schema(self, tool_name: str) -> Dict[str, Any]:
            """Get mock tool schema.

        Args:
            tool_name: Name of the tool

        Returns:
            Mock tool schema
        """
        return {
            "name": tool_name,
            "description": f"Mock tool: {tool_name}",
            "parameters": {
                "query": {"type": "string", "required": True},
                "options": {"type": "object", "required": False},
            },
            "mock": True,
        }

    def get_capabilities(self) -> List[ActionCapability]:
            """Get mock capabilities.

        Returns:
            All action capabilities
        """
        return list(ActionCapability)

    def reset(self) -> None:
            """Reset mock state."""
        self.call_history.clear()
