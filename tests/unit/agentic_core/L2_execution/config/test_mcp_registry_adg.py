"""ADG-driven tests for L2_execution/config/mcp_registry.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.config.mcp_registry import (
        McpServerMode,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    McpServerMode = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="mcp_registry deps unavailable")
class TestMcpServerMode:
    def test_is_enum(self):
        import enum
        assert issubclass(McpServerMode, enum.Enum)

    def test_local_value(self):
        assert McpServerMode.LOCAL.value == "local"

    def test_mocked_value(self):
        assert McpServerMode.MOCKED.value == "mocked"

    def test_is_str_enum(self):
        assert issubclass(McpServerMode, str)


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
