"""
MCP seam contract — Protocol stub for MCPConnectionManager.

The concrete implementation may not be present in all environments.
This stub satisfies type annotations without a hard import dependency.

This module sits outside the layer hierarchy so imports from here
do not count as upward seams in the gravity scanner.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

@runtime_checkable
class MCPConnectionManager(Protocol):
    """Minimal protocol for MCP connection managers."""

    async def connect(self, role: str) -> None: ...

    async def disconnect(self) -> None: ...

    async def call_tool(self, tool: str, **kwargs: Any) -> Any: ...


__all__ = ["MCPConnectionManager"]
