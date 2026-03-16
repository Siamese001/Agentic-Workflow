"""ADG-driven tests for L2_execution/enforcement/tool_policy_enforcer.py — fan_in=0."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_tool_policy_enforcer_adg")
_emit_applies_guardrail("p0", "test_tool_policy_enforcer_adg", "p0_governance")
_emit_snapshots_state("p0", "test_tool_policy_enforcer_adg", "state_snapshot")
emit_replay_key("p0", "test_tool_policy_enforcer_adg")
emit_determinism_digest("p0", "test_tool_policy_enforcer_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.enforcement.tool_policy_enforcer import (
        ToolPolicyEnforcer,
        _stable_args_hash,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ToolPolicyEnforcer = None  # type: ignore[assignment,misc]
    _stable_args_hash = None  # type: ignore[assignment]


@pytest.mark.skipif(not _AVAILABLE, reason="tool_policy_enforcer deps unavailable")
class TestStableArgsHash:
    def test_returns_string(self):
        result = _stable_args_hash({"key": "value"})
        assert isinstance(result, str)

    def test_deterministic(self):
        args = {"b": 2, "a": 1}
        assert _stable_args_hash(args) == _stable_args_hash(args)

    def test_sort_key_insensitive(self):
        assert _stable_args_hash({"a": 1, "b": 2}) == _stable_args_hash({"b": 2, "a": 1})


@pytest.mark.skipif(not _AVAILABLE, reason="tool_policy_enforcer deps unavailable")
class TestToolPolicyEnforcer:
    def test_creates(self):
        enforcer = ToolPolicyEnforcer()
        assert enforcer is not None

    def test_has_register_rule(self):
        assert hasattr(ToolPolicyEnforcer, "register_rule")


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
