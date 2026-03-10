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

# NOT_AN_AGENT - This is a foundational CLASS, not a runtime agent
"""
L2ExecutionBase - Consolidated Base for L2 Execution Agents

Layer: L2 - Execution
Responsibilities:
- Tool registry operations
- MCP (Model Context Protocol) handling
- Action execution and coordination
- External API interactions

MRO HARDENING:
- Inheritance order: SovereignBaseAgent (root)
- All L2 agents inherit from this base for consistent execution capabilities
"""

from dataclasses import dataclass
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L0_routing.enforcement.runtime_guard import (
    runtime_guard,
)


@dataclass
class L2ExecutionBase(SovereignBaseAgent):
    """
    Consolidated base for L2 Execution agents.

    L2 agents handle:
    - Tool registry management
    - MCP protocol operations
    - Action execution pipelines
    - External service integration

    MRO: L2ExecutionBase -> SovereignBaseAgent -> object
    """

    name: str = "L2ExecutionBase"
    layer: str = "L2"

    def __post_init__(self) -> None:
        """Cooperative MRO initialization."""
        super().__post_init__()

    @runtime_guard("B.execute_tool.L2ExecutionBase")
    def execute_tool(self, tool_name: str, **kwargs: Any) -> dict[str, Any]:
        """
        Execute a registered tool by name.

        Override in subclasses for specialized tool execution.
        """
        return {"tool": tool_name, "status": "not_implemented", "result": None}

    def register_tool(self, tool_name: str, tool_func: Any) -> bool:
        """
        Register a tool in the tool registry.

        Override in subclasses for specialized tool registration.
        """
        return False
