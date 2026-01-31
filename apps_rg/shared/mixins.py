"""
Shared mixins for RG agents - extracted to avoid circular dependencies.

These mixins are used by both StateTransaction and engine agents.
Extracted here to break circular dependency chain.
"""

from __future__ import annotations


class MCPHardenedMixin:
    """MCP hardening mixin for RG agents."""

    def __init__(self):
        self._mcp_hardened = True


class HealerMixin:
    """Healing mixin for RG agents."""

    def __init__(self):
        self._healing_enabled = False
