"""
MCPHardenedMixin - Backwards Compatibility Shim

[MIXIN REFACTOR] All hardened MCP logic has been consolidated into
MCPOperationMixin (mcp_operation_mixin.py). This file re-exports the
class under the old name to preserve 89+ existing import sites.

Canonical location: agentic_core.mixins.mcp_operation_mixin.MCPOperationMixin
"""

from agentic_core.mixins.mcp_operation_mixin import MCPOperationMixin


class MCPHardenedMixin(MCPOperationMixin):
    """Backwards-compat alias. Use MCPOperationMixin directly for new code."""

    pass


mcp_hardened_mixin = MCPHardenedMixin
