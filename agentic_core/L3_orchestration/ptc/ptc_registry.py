"""
Programmatic Tool Calling (PTC) - Tool Registry

Deterministic registry for tool specifications and handlers.
Enforces uniqueness, validation, and deterministic ordering.
"""

from __future__ import annotations

import builtins
from typing import Callable

from .tool_contract import ToolSpec


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class ToolRegistry:
    """Deterministic registry for tools."""

    def __init__(self) -> None:
        """Initialize empty registry."""
        self._specs: dict[str, ToolSpec] = {}
        self._handlers: dict[str, Callable] = {}

    def register(self, spec: ToolSpec, handler: Callable) -> None:
        """Register a tool with specification and handler.

        Args:
            spec: Tool specification
            handler: Handler function

        Raises:
            ValueError: If tool_id already exists or validation fails
        """
        # Validate tool_id uniqueness
        if spec.tool_id in self._specs:
            raise ValueError(f"Tool '{spec.tool_id}' already registered")

        # Validate side effect class
        valid_side_effects = {"PURE", "READONLY", "WRITE_FS", "SUBPROCESS"}
        if spec.side_effect_class not in valid_side_effects:
            raise ValueError(f"Invalid side_effect_class: {spec.side_effect_class}")

        # Validate args are sorted by name (enforced by ToolSpec.__post_init__)
        arg_names = [arg.name for arg in spec.args]
        if arg_names != sorted(arg_names):
            raise ValueError("ToolSpec args must be sorted by name")

        # Validate version
        if spec.version < 1:
            raise ValueError("ToolSpec version must be >= 1")

        # Register
        self._specs[spec.tool_id] = spec
        self._handlers[spec.tool_id] = handler

    def get(self, tool_id: str) -> tuple[ToolSpec, Callable]:
        """Get tool specification and handler.

        Args:
            tool_id: Tool identifier

        Returns:
            Tuple of (spec, handler)

        Raises:
            ValueError: If tool_id not found
        """
        if tool_id not in self._specs:
            raise ValueError(f"Tool '{tool_id}' not found")

        return self._specs[tool_id], self._handlers[tool_id]

    def list(self) -> builtins.list[ToolSpec]:
        """List all registered tool specifications.

        Returns:
            List of ToolSpec objects sorted by tool_id
        """
        specs = list(self._specs.values())
        specs.sort(key=lambda s: s.tool_id)
        return specs

    def has(self, tool_id: str) -> bool:
        """Check if tool is registered.

        Args:
            tool_id: Tool identifier

        Returns:
            True if tool exists
        """
        return tool_id in self._specs

    def count(self) -> int:
        """Get number of registered tools.

        Returns:
            Number of tools
        """
        return len(self._specs)


# =============================================================================
# Global Registry Instance
# =============================================================================

# Global registry for built-in tools
_GLOBAL_REGISTRY = ToolRegistry()


def get_global_registry() -> ToolRegistry:
    """Get the global tool registry.

    Returns:
        Global ToolRegistry instance
    """
    return _GLOBAL_REGISTRY


def register_tool(spec: ToolSpec, handler: Callable) -> None:
    """Register a tool in the global registry.

    Args:
        spec: Tool specification
        handler: Handler function
    """
    _GLOBAL_REGISTRY.register(spec, handler)


def get_tool(tool_id: str) -> tuple[ToolSpec, Callable]:
    """Get tool from global registry.

    Args:
        tool_id: Tool identifier

    Returns:
        Tuple of (spec, handler)
    """
    return _GLOBAL_REGISTRY.get(tool_id)


def list_tools() -> list[ToolSpec]:
    """List all tools in global registry.

    Returns:
        List of ToolSpec objects
    """
    return _GLOBAL_REGISTRY.list()


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "ToolRegistry",
    "get_global_registry",
    "register_tool",
    "get_tool",
    "list_tools",
]
