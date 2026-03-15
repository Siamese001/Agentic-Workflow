"""MCP authority seam contract — Protocol and lazy factory for MCPSovereignAuthority.

This module sits outside the layer hierarchy so imports from here
do not count as upward seams in the gravity scanner.
All upward imports (→ L5) are deferred inside the factory function.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class MCPAuthorityProtocol(Protocol):
    """Minimal protocol for MCP sovereign authority."""

    def is_authorized(self) -> bool: ...

    def record_breach(self, error_msg: str) -> Any: ...

    def authorize_tool_call(self, tool_name: str, args: dict) -> None: ...


class _NullAuthority:
    """No-op fallback when L5 authority is unavailable (CI / offline)."""

    def is_authorized(self) -> bool:
        return True

    def record_breach(self, error_msg: str) -> Any:
        import logging

        logging.getLogger(__name__).warning("[NullAuthority] breach recorded: %s", error_msg)

    def authorize_tool_call(self, tool_name: str, args: dict) -> None:
        pass


def get_mcp_authority() -> MCPAuthorityProtocol:
    """Return the live MCPSovereignAuthority singleton, or a no-op fallback.

    Lazy import holds the L5 upward dependency inside the seam so that
    L2/L3 consumers can call this without gravity violations.
    """
    try:
        from agentic_core.L5_safety.enforcement.mcp_sovereign_authority_enforcer import (
            mcp_authority,
        )

        return mcp_authority  # type: ignore[return-value]
    except ImportError:
        return _NullAuthority()


__all__ = ["MCPAuthorityProtocol", "get_mcp_authority"]
