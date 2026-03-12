"""
MCP seam contract — Protocol stub for MCPConnectionManager.

The concrete implementation may not be present in all environments.
This stub satisfies type annotations without a hard import dependency.

This module sits outside the layer hierarchy so imports from here
do not count as upward seams in the gravity scanner.
"""
from __future__ import annotations
from typing import Any, Protocol, runtime_checkable
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

@runtime_checkable
class MCPConnectionManager(Protocol):
    """Minimal protocol for MCP connection managers."""

    async def connect(self, role: str) -> None:
        ...

    async def disconnect(self) -> None:
        ...

    async def call_tool(self, tool: str, **kwargs: Any) -> Any:
        ...
__all__ = ['MCPConnectionManager']
