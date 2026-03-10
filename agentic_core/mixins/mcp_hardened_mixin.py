"""
MCPHardenedMixin - Backwards Compatibility Shim

[MIXIN REFACTOR] All hardened MCP logic has been consolidated into
MCPOperationMixin (mcp_operation_mixin.py). This file re-exports the
class under the old name to preserve 89+ existing import sites.

Canonical location: agentic_core.mixins.mcp_operation_mixin.MCPOperationMixin
"""

from agentic_core.mixins.mcp_operation_mixin import MCPOperationMixin


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class MCPHardenedMixin(MCPOperationMixin):
    """Backwards-compat alias. Use MCPOperationMixin directly for new code."""

    pass


# snake_case alias used by some import sites
mcp_hardened_mixin = MCPHardenedMixin
