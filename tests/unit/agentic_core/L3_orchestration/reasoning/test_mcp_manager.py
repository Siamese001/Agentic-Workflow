"""Foundational behavioral tests for agentic_core/L3_orchestration/reasoning/mcp_manager.py."""

from __future__ import annotations

import builtins
from unittest.mock import MagicMock, patch

import pytest


def test_module_importable():
    """Module mcp_manager must be importable."""


class TestResolveToolDynamicDiscovery:
    """_resolve_tool must find mcp{N}_{tool_name} builtins regardless of index.

    Resolution contract:
      - Supported range: mcp0_ through mcp19_ (indices 0-19 inclusive)
      - First match wins; lower index has priority
      - Wrong-prefix noise (xmcp3_, mcpX_) is not matched
      - Unknown tool returns None
    """

    def test_resolve_tool_finds_at_index_0(self):
        from agentic_core.L3_orchestration.reasoning.mcp_manager import _resolve_tool

        mock_fn = MagicMock()
        with patch.dict(vars(builtins), {"mcp0_some_tool": mock_fn}):
            result = _resolve_tool("some_tool")
        assert result is mock_fn

    def test_resolve_tool_finds_at_index_19(self):
        from agentic_core.L3_orchestration.reasoning.mcp_manager import _resolve_tool

        mock_fn = MagicMock()
        with patch.dict(vars(builtins), {"mcp19_some_tool": mock_fn}):
            result = _resolve_tool("some_tool")
        assert result is mock_fn

    def test_resolve_tool_ignores_wrong_prefix_noise(self):
        from agentic_core.L3_orchestration.reasoning.mcp_manager import _resolve_tool

        mock_fn = MagicMock()
        with patch.dict(vars(builtins), {"xmcp3_http_get": mock_fn}):
            result = _resolve_tool("http_get")
        assert result is None

    def test_resolve_tool_finds_mcp_prefixed_builtin_at_known_index(self):
        from agentic_core.L3_orchestration.reasoning.mcp_manager import _resolve_tool

        mock_fn = MagicMock()
        with patch.dict(vars(builtins), {"mcp3_http_get": mock_fn}):
            result = _resolve_tool("http_get")
        assert result is mock_fn

    def test_resolve_tool_finds_mcp_prefixed_builtin_at_arbitrary_index(self):
        from agentic_core.L3_orchestration.reasoning.mcp_manager import _resolve_tool

        mock_fn = MagicMock()
        with patch.dict(vars(builtins), {"mcp11_batch_requests": mock_fn}):
            result = _resolve_tool("batch_requests")
        assert result is mock_fn

    def test_resolve_tool_returns_none_for_unknown_tool(self):
        from agentic_core.L3_orchestration.reasoning.mcp_manager import _resolve_tool

        result = _resolve_tool("__no_such_tool_xyzzy__")
        assert result is None


class TestCallToolExplicitError:
    """call_tool must return an explicit error dict for unresolved tools, not {}."""

    @pytest.mark.asyncio
    async def test_call_tool_explicit_error_for_unresolved_tool(self):
        from agentic_core.L3_orchestration.reasoning.mcp_manager import MCPConnectionManager

        mgr = MCPConnectionManager()
        result = await mgr.call_tool("__no_such_tool_xyzzy__")
        assert isinstance(result, dict)
        assert "error" in result
        assert "tool_not_found" in result["error"]
        assert result.get("available") is False

    @pytest.mark.asyncio
    async def test_call_tool_invokes_resolved_function(self):
        from agentic_core.L3_orchestration.reasoning.mcp_manager import MCPConnectionManager

        mock_fn = MagicMock(return_value={"status": "ok"})
        mgr = MCPConnectionManager()
        with patch.dict(vars(builtins), {"mcp3_http_get": mock_fn}):
            result = await mgr.call_tool("http_get", {"url": "https://example.com"})
        mock_fn.assert_called_once_with(url="https://example.com")
        assert result == {"status": "ok"}
