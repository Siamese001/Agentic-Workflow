"""ADG-driven tests for L0_routing/scripts/action_capability.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L0_routing.scripts.action_capability import (
    ActionCapability,
    ActionRequest,
)


class TestActionCapability:
    def test_is_enum(self):
        import enum
        assert issubclass(ActionCapability, enum.Enum)

    def test_has_tool_execution(self):
        assert ActionCapability.TOOL_EXECUTION.value == "tool_execution"

    def test_has_file_operations(self):
        assert ActionCapability.FILE_OPERATIONS.value == "file_operations"

    def test_all_values_are_strings(self):
        for cap in ActionCapability:
            assert isinstance(cap.value, str)


class TestActionRequest:
    def test_creates_with_defaults(self):
        req = ActionRequest(action_type="run", tool_name="bash")
        assert req.action_type == "run"
        assert req.tool_name == "bash"
        assert req.timeout_ms == 30000
        assert req.parameters == {}

    def test_creates_with_params(self):
        req = ActionRequest(
            action_type="run",
            tool_name="python",
            parameters={"cmd": "print('hi')"},
        )
        assert req.parameters["cmd"] == "print('hi')"

    def test_has_to_dict(self):
        assert hasattr(ActionRequest, "to_dict")
