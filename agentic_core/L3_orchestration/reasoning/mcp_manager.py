from __future__ import annotations

import builtins
import inspect
from typing import Any, Callable


def _resolve_tool(tool_name: str) -> Callable[..., Any] | None:
    normalized_name = str(tool_name or "").strip()
    if not normalized_name:
        return None
    for index in range(20):
        candidate = getattr(builtins, f"mcp{index}_{normalized_name}", None)
        if callable(candidate):
            return candidate
    return None


def _normalize_params(params: Any) -> dict[str, Any]:
    if params is None:
        return {}
    if isinstance(params, dict):
        return dict(params)
    return {"value": params}


class MCPConnectionManager:
    async def call_tool(self, tool_name: str, params: dict[str, Any] | None = None) -> Any:
        normalized_tool = str(tool_name or "").strip()
        normalized_params = _normalize_params(params)
        fn = _resolve_tool(normalized_tool)
        if fn is None:
            return {"error": f"tool_not_found:{normalized_tool}", "available": False}
        try:
            result = fn(**normalized_params)
            if inspect.isawaitable(result):
                result = await result
            return result
        except Exception as exc:  # guardian: allow-broad-exception -- MCP tool call boundary: returns error dict instead of raising
            return {
                "error": f"tool_call_failed:{normalized_tool}:{exc}",
                "available": True,
                "tool_name": normalized_tool,
            }
