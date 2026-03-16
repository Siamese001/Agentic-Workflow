"""ADG-driven tests for L0_routing/scripts/action_capability.py — fan_in=0."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_action_capability_adg")
_emit_applies_guardrail("p0", "test_action_capability_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_action_capability_adg", "policy_binding")
_emit_snapshots_state("p0", "test_action_capability_adg", "state_snapshot")
emit_replay_key("p0", "test_action_capability_adg")
emit_determinism_digest("p0", "test_action_capability_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
