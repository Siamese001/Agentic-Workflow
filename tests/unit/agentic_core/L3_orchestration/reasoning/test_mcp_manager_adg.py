"""ADG-driven tests for agentic_core/L3_orchestration/reasoning/mcp_manager.py — fan_in=5.

Contract tests: _TOOL_DISPATCH, _resolve_tool, MCPConnectionManager, load_mcp_config.
"""
from __future__ import annotations

import asyncio
import json
import tempfile
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L3_orchestration.reasoning.mcp_manager import (
    MCPConnectionManager,
    _TOOL_DISPATCH,
    _resolve_tool,
    load_mcp_config,
)


class TestToolDispatchTable:
    def test_dispatch_is_dict(self):
        assert isinstance(_TOOL_DISPATCH, dict)

    def test_read_file_mapped(self):
        assert "read_file" in _TOOL_DISPATCH

    def test_write_file_mapped(self):
        assert "write_file" in _TOOL_DISPATCH

    def test_brave_search_mapped(self):
        assert "brave_search" in _TOOL_DISPATCH

    def test_playwright_navigate_mapped(self):
        assert "playwright_navigate" in _TOOL_DISPATCH

    def test_all_values_are_strings(self):
        for k, v in _TOOL_DISPATCH.items():
            assert isinstance(v, str), f"{k} → {v!r} should be str"


class TestResolveTool:
    def test_unknown_tool_returns_none(self):
        result = _resolve_tool("nonexistent_tool_xyz")
        assert result is None

    def test_returns_none_for_unmapped(self):
        result = _resolve_tool("totally_unknown_abc")
        assert result is None

    def test_does_not_raise_for_any_dispatch_key(self):
        for key in _TOOL_DISPATCH:
            _resolve_tool(key)  # must not raise


class TestMCPConnectionManagerInit:
    def test_creates_without_args(self):
        manager = MCPConnectionManager()
        assert manager is not None

    def test_config_defaults_empty(self):
        manager = MCPConnectionManager()
        assert manager._config == {}

    def test_role_defaults(self):
        manager = MCPConnectionManager()
        assert manager._role == "default"

    def test_connected_starts_false(self):
        manager = MCPConnectionManager()
        assert manager._connected is False

    def test_creates_with_config(self):
        manager = MCPConnectionManager(config={"timeout": 30})
        assert manager._config == {"timeout": 30}


class TestMCPConnectionManagerAsync:
    def test_connect_sets_role(self):
        manager = MCPConnectionManager()
        asyncio.run(manager.connect("test_role"))
        assert manager._role == "test_role"
        assert manager._connected is True

    def test_disconnect_sets_false(self):
        manager = MCPConnectionManager()
        asyncio.run(manager.connect("test_role"))
        asyncio.run(manager.disconnect())
        assert manager._connected is False

    def test_call_tool_unknown_returns_empty_dict(self):
        manager = MCPConnectionManager()
        result = asyncio.run(manager.call_tool("nonexistent_tool_xyz", {}))
        assert result == {}

    def test_cleanup_disconnects(self):
        manager = MCPConnectionManager()
        asyncio.run(manager.connect("role"))
        asyncio.run(manager.cleanup())
        assert manager._connected is False


class TestLoadMcpConfig:
    def test_missing_file_returns_empty_dict(self):
        result = load_mcp_config("/nonexistent_xyz_abc/mcp_config.json")
        assert result == {}

    def test_loads_json_file(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump({"key": "value"}, f)
            tmp = f.name
        try:
            result = load_mcp_config(tmp)
            assert result == {"key": "value"}
        finally:
            Path(tmp).unlink(missing_ok=True)

    def test_returns_empty_dict_for_invalid_json(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            f.write("{ invalid json }")
            tmp = f.name
        try:
            result = load_mcp_config(tmp)
            assert result == {}
        finally:
            Path(tmp).unlink(missing_ok=True)

    def test_returns_empty_dict_for_empty_json(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            f.write("{}")
            tmp = f.name
        try:
            result = load_mcp_config(tmp)
            assert result == {}
        finally:
            Path(tmp).unlink(missing_ok=True)
