from __future__ import annotations

"""L3 Orchestration: Concrete MCPConnectionManager + load_mcp_config.

Routes call_tool() dispatches to the live Windsurf MCP tool functions
available in the environment (mcp8_*, mcp12_*, mcp1_*, mcp11_*).
Falls back gracefully when a tool is unavailable.
"""

import json
import logging
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

Logger: Any = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tool dispatch table  — maps logical tool names to live Windsurf callables.
# Each entry is resolved lazily so missing tools never crash at import time.
# ---------------------------------------------------------------------------

_TOOL_DISPATCH: dict[str, str] = {
    # Filesystem (mcp8_*)
    "read_file": "mcp8_read_text_file",
    "write_file": "mcp8_write_file",
    "edit_file": "mcp8_edit_file",
    "move_file": "mcp8_move_file",
    "create_directory": "mcp8_create_directory",
    "list_directory": "mcp8_list_directory",
    # Memory (mcp11_*)
    "create_entities": "mcp11_create_entities",
    "create_relations": "mcp11_create_relations",
    "add_observations": "mcp11_add_observations",
    "search_nodes": "mcp11_search_nodes",
    "read_graph": "mcp11_read_graph",
    # Brave Search (mcp1_*)
    "brave_search": "mcp1_brave_web_search",
    "brave_web_search": "mcp1_brave_web_search",
    "brave_local_search": "mcp1_brave_local_search",
    # Playwright (mcp8_* — current Windsurf registration prefix)
    "playwright_navigate": "mcp8_playwright_navigate",
    "playwright_screenshot": "mcp8_playwright_screenshot",
    "playwright_get_text": "mcp8_playwright_get_visible_text",
    "playwright_click": "mcp8_playwright_click",
    "playwright_fill": "mcp8_playwright_fill",
    "playwright_get_html": "mcp8_playwright_get_visible_html",
    "playwright_press_key": "mcp8_playwright_press_key",
    # Redis operations (adg_redis custom server)
    "redis_get": "redis_get",
    "redis_set": "redis_set",
    "redis_delete": "redis_delete",
    # Fetch (mcp4_*)
    "fetch": "mcp4_fetch",
    # DeepWiki (mcp3_*)
    "deepwiki_ask": "mcp3_ask_question",
    "deepwiki_structure": "mcp3_read_wiki_structure",
    # Sequential thinking
    "sequential_thinking": "mcp8_sequentialthinking",
}


def _resolve_tool(tool_name: str) -> Any:
    """Resolve a logical tool name to a callable, or None if unavailable."""
    mapped = _TOOL_DISPATCH.get(tool_name)
    if mapped is None:
        Logger.debug(f"[MCPManager] No dispatch mapping for tool '{tool_name}'")
        return None

    # Try to resolve via global builtins (Windsurf injects MCP tools as globals)
    import builtins

    fn = getattr(builtins, mapped, None)
    if fn is not None:
        return fn

    # Try current module globals (some environments inject here)
    import sys

    frame_globals = sys.modules.get("__main__", None)
    if frame_globals is not None:
        fn = getattr(frame_globals, mapped, None)
        if fn is not None:
            return fn

    Logger.debug(f"[MCPManager] Tool '{mapped}' not found in environment")
    return None


class MCPConnectionManager:
    """
    Concrete implementation of the MCPConnectionManager Protocol.

    Routes call_tool() to live Windsurf MCP tool functions.
    All calls are resilient: errors are logged, None is returned on failure.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self._config = config or {}
        self._role: str = "default"
        self._connected = False

    async def connect(self, role: str) -> None:
        """Mark connection active for the given role."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "MCPConnectionManager.connect")

        self._role = role
        self._connected = True
        Logger.info(f"[MCPManager] Connected for role '{role}'")

    async def disconnect(self) -> None:
        """Mark connection inactive."""
        self._connected = False
        Logger.info("[MCPManager] Disconnected")

    async def call_tool(self, tool: str, args: dict[str, Any] | None = None, **kwargs: Any) -> Any:
        """
        Dispatch a logical tool call to the live MCP tool function.

        Args:
            tool: Logical tool name (see _TOOL_DISPATCH)
            args: Tool arguments dict (merged with kwargs)

        Returns:
            Tool result or empty dict on failure
        """
        merged = {**(args or {}), **kwargs}
        fn = _resolve_tool(tool)
        if fn is None:
            Logger.warning(f"[MCPManager] Tool '{tool}' unavailable — returning empty result")
            return {}
        try:
            result = fn(**merged)
            # Support both sync and async callables
            if hasattr(result, "__await__"):
                import asyncio

                result = await asyncio.ensure_future(result)
            Logger.debug(f"[MCPManager] Tool '{tool}' succeeded")
            return result if result is not None else {}
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.error(f"[MCPManager] Tool '{tool}' failed: {e}")
            return {"error": str(e)}

    async def cleanup(self) -> None:
        """Alias for disconnect."""
        await self.disconnect()


def load_mcp_config(config_path: str) -> dict[str, Any]:
    """
    Load MCP configuration from a YAML or JSON file.

    Falls back to empty config dict if file is missing or unparseable.
    """
    path = Path(config_path)
    # guardian: allow-config-with-logic
    if not path.exists():
        Logger.warning(f"[MCPManager] Config file not found: {config_path} — using defaults")
        return {}
    try:
        text = path.read_text(encoding="utf-8")
        # guardian: allow-config-with-logic
        if path.suffix in {".yaml", ".yml"}:
            try:
                import yaml  # type: ignore[import]

                return yaml.safe_load(text) or {}
            except ImportError:
                Logger.warning("[MCPManager] PyYAML not installed — falling back to JSON parse")
        return json.loads(text)
    # guardian: allow-silent-swallow
    except Exception as e:
        Logger.warning(f"[MCPManager] Failed to parse config {config_path}: {e} — using defaults")
        return {}
