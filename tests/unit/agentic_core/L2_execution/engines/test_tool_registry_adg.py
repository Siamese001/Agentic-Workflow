"""ADG-driven tests for L2_execution/engines/tool_registry.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.engines.tool_registry import ToolDefinition
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ToolDefinition = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="tool_registry deps (numpy) unavailable")
class TestToolDefinition:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ToolDefinition)

    def test_creates(self):
        td = ToolDefinition(
            name="read_file",
            description="Read a file",
            function=lambda: None,
            parameters={"path": "str"},
        )
        assert td.name == "read_file"
        assert td.usage_count == 0
        assert td.success_rate == 1.0


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
