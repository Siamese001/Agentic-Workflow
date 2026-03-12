"""ADG-driven tests for L2_execution/types/mcp_error_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.types.mcp_error_types import (
    MCPError,
    MCPClientInitializationError,
    MCPClientNotFoundError,
)


class TestMCPError:
    def test_is_exception(self):
        assert issubclass(MCPError, Exception)


class TestMCPClientInitializationError:
    def test_is_mcp_error(self):
        assert issubclass(MCPClientInitializationError, MCPError)

    def test_creates(self):
        err = MCPClientInitializationError("init failed", client_name="fs", Provider="mcp8")
        assert err.client_name == "fs"
        assert err.Provider == "mcp8"
        assert "init failed" in str(err)


class TestMCPClientNotFoundError:
    def test_is_mcp_error(self):
        assert issubclass(MCPClientNotFoundError, MCPError)

    def test_creates(self):
        err = MCPClientNotFoundError("not found", client_name="unknown")
        assert err.client_name == "unknown"
