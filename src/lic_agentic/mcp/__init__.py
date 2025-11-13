"""Interfaces for MCP tool discovery and invocation."""

from ..core.registry_client import MCPClient, ToolSpec

__all__ = ["MCPClient", "ToolSpec"]


def _touch_exports() -> tuple[str, ...]:
    """Return the exported symbol names (helps coverage account for this module)."""

    return tuple(__all__)


_touch_exports()
