from __future__ import annotations

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""
Action Node - Sub-atomic Execution & Output Generation

Handles tool selection, execution, and output formatting.
Isolated from perception and reasoning logic.
"""


import asyncio
import time
from typing import Any


class ActionNode:
    """
    Sub-atomic action node - tool execution and output generation.

    Responsibilities:
    - Select appropriate tools
    - Execute tools
    - Format output
    - Handle execution errors
    """

    def __init__(self):
        """Initialize action node."""
        self.actions_executed = 0
        self.tools_used = 0
        self.total_execution_time = 0.0

    def act(self, reasoning: dict[str, Any]) -> dict[str, Any]:
        """
        Execute action based on reasoning.

        Args:
            reasoning: Reasoning result from ReasoningNode

        Returns:
            Action result with output and metadata
        """
        start_time = time.time()
        self.actions_executed += 1

        # Select tools based on plan
        tools = self._select_tools(reasoning["plan"])

        # Execute tools
        results = self._execute_tools(tools, reasoning)

        # Format output
        output = self._format_output(results, reasoning)

        execution_time = time.time() - start_time
        self.total_execution_time += execution_time

        action_result = {
            "output": output,
            "tools_used": [t["name"] for t in tools],
            "tool_count": len(tools),
            "execution_time": execution_time,
            "success": True,
        }

        return action_result

    async def act_async(self, reasoning: dict[str, Any]) -> dict[str, Any]:
        """
        Asynchronous action execution.

        Args:
            reasoning: Reasoning result

        Returns:
            Action result
        """
        start_time = time.time()
        self.actions_executed += 1

        # Select tools (fast)
        tools = self._select_tools(reasoning["plan"])

        # Execute tools asynchronously
        results = await asyncio.to_thread(self._execute_tools, tools, reasoning)

        # Format output
        output = await asyncio.to_thread(self._format_output, results, reasoning)

        execution_time = time.time() - start_time
        self.total_execution_time += execution_time

        action_result = {
            "output": output,
            "tools_used": [t["name"] for t in tools],
            "tool_count": len(tools),
            "execution_time": execution_time,
            "success": True,
        }

        return action_result

    def act_simple(self, perceived: dict[str, Any]) -> dict[str, Any]:
        """
        Simple action for low-complexity intents (lazy evaluation).

        Args:
            perceived: Perceived state

        Returns:
            Simple action result
        """
        start_time = time.time()
        self.actions_executed += 1

        # Direct response without heavy reasoning
        output = f"Responding to: {perceived['query'][:50]}..."

        execution_time = time.time() - start_time
        self.total_execution_time += execution_time

        return {
            "output": output,
            "tools_used": [],
            "tool_count": 0,
            "execution_time": execution_time,
            "success": True,
            "simple": True,
        }

    def _select_tools(self, plan: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Select tools based on execution plan.

        Args:
            plan: Execution plan from ReasoningNode

        Returns:
            List of selected tools
        """
        tools = []

        # Simple tool selection based on plan steps
        step_count = len(plan.get("steps", []))

        if step_count > 0:
            # Primary tool
            tools.append({"name": "primary_executor", "type": "execution", "priority": 1})
            self.tools_used += 1

        if step_count > 2:
            # Secondary tool for complex plans
            tools.append({"name": "secondary_executor", "type": "support", "priority": 2})
            self.tools_used += 1

        return tools

    def _execute_tools(self, tools: list[dict[str, Any]], reasoning: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Execute selected tools.

        Args:
            tools: Selected tools
            reasoning: Reasoning context

        Returns:
            Tool execution results
        """
        results = []

        for tool in tools:
            result = {
                "tool": tool["name"],
                "status": "success",
                "output": f"Executed {tool['name']}",
                "metadata": {
                    "type": tool.get("type", "unknown"),
                    "priority": tool.get("priority", 0),
                },
            }
            results.append(result)

        return results

    def _format_output(self, results: list[dict[str, Any]], reasoning: dict[str, Any]) -> str:
        """
        Format final output from tool results.

        Args:
            results: Tool execution results
            reasoning: Reasoning context

        Returns:
            Formatted output string
        """
        if not results:
            return "No tools executed"

        # Build output from results
        output_parts = []

        for result in results:
            if result.get("status") == "success":
                output_parts.append(result.get("output", ""))

        # Add reasoning summary
        thoughts = reasoning.get("thoughts", [])
        if thoughts:
            output_parts.append(f"Based on {len(thoughts)} thoughts")

        return " | ".join(output_parts) if output_parts else "Execution completed"

    def get_statistics(self) -> dict[str, Any]:
        """Get action statistics."""
        avg_execution_time = (
            self.total_execution_time / self.actions_executed if self.actions_executed > 0 else 0.0
        )

        return {
            "actions_executed": self.actions_executed,
            "tools_used": self.tools_used,
            "total_execution_time": self.total_execution_time,
            "avg_execution_time": avg_execution_time,
        }
