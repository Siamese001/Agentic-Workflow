"""Shim: re-exports ToolRegistry from its canonical location.

Canonical source: agentic_core.L2_execution.engines.l2_tool_registry
"""

from agentic_core.L2_execution.reasoning.l2_tool_registry import (
    ToolDefinition,
    ToolMatch,
    create_tool_registry,
)
from agentic_core.L2_execution.reasoning.l2_tool_registry import (  # noqa: F401
    tool_registry as ToolRegistry,
)

__all__ = ["ToolRegistry", "ToolDefinition", "ToolMatch", "create_tool_registry"]
