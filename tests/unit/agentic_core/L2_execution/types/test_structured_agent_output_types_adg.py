"""ADG-driven tests for L2_execution/types/structured_agent_output_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.types.structured_agent_output_types import (
    StructuredOutputViolation,
    ToolRequest,
)


class TestStructuredOutputViolation:
    def test_is_value_error(self):
        assert issubclass(StructuredOutputViolation, ValueError)


class TestToolRequest:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ToolRequest)

    def test_is_frozen(self):
        tr = ToolRequest(tool_name="read_file", args={"path": "x"})
        with pytest.raises((AttributeError, TypeError)):
            tr.tool_name = "write_file"

    def test_creates_with_name(self):
        tr = ToolRequest(tool_name="read_file")
        assert tr.tool_name == "read_file"
        assert tr.args == {}

    def test_empty_tool_name_raises(self):
        with pytest.raises((ValueError, Exception)):
            ToolRequest(tool_name="")
