"""ADG-driven tests for L2 enforcement modules — fan_in=1.

Covers: healer_pipe_order, tool_policy_enforcer.
"""
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

_emit_records_execution_trace("p0", "evidence", "test_l2_enforcement_adg")
_emit_applies_guardrail("p0", "test_l2_enforcement_adg", "p0_governance")
_emit_snapshots_state("p0", "test_l2_enforcement_adg", "state_snapshot")
emit_replay_key("p0", "test_l2_enforcement_adg")
emit_determinism_digest("p0", "test_l2_enforcement_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# healer_pipe_order
# ---------------------------------------------------------------------------
from agentic_core.L2_execution.enforcement.healer_pipe_order import (
    enforce_healer_pipe_order,
)

_CANONICAL_10 = (
    "pre_audit",
    "discovery",
    "reconciliation",
    "alignment",
    "arch_validation",
    "healing",
    "certification",
    "post_audit",
    "cleanup",
    "report",
)


class TestHealerPipeOrder:
    def test_enforce_callable(self):
        assert callable(enforce_healer_pipe_order)

    def test_passes_on_exact_match(self):
        enforce_healer_pipe_order(
            expected_steps=_CANONICAL_10,
            observed_steps=list(_CANONICAL_10),
        )

    def test_raises_on_wrong_length(self):
        with pytest.raises(PermissionError):
            enforce_healer_pipe_order(
                expected_steps=_CANONICAL_10,
                observed_steps=list(_CANONICAL_10)[:-1],
            )

    def test_raises_on_extra_step(self):
        with pytest.raises(PermissionError):
            enforce_healer_pipe_order(
                expected_steps=_CANONICAL_10,
                observed_steps=list(_CANONICAL_10) + ["extra"],
            )

    def test_raises_on_wrong_order(self):
        reordered = list(_CANONICAL_10)
        reordered[0], reordered[1] = reordered[1], reordered[0]
        with pytest.raises(PermissionError):
            enforce_healer_pipe_order(
                expected_steps=_CANONICAL_10,
                observed_steps=reordered,
            )

    def test_requires_exactly_10_expected_steps(self):
        with pytest.raises(AssertionError):
            enforce_healer_pipe_order(
                expected_steps=("only_one",),
                observed_steps=["only_one"],
            )

    def test_trace_id_accepted(self):
        enforce_healer_pipe_order(
            expected_steps=_CANONICAL_10,
            observed_steps=list(_CANONICAL_10),
            trace_id="test-trace-001",
        )


# ---------------------------------------------------------------------------
# tool_policy_enforcer
# ---------------------------------------------------------------------------
from agentic_core.L2_execution.enforcement.tool_policy_enforcer import (
    ToolPolicyEnforcer,
    _stable_args_hash,
)
from agentic_core.L2_execution.types.tool_enforcement_types import (
    LawSlotOutcome,
)


class TestStableArgsHash:
    def test_returns_string(self):
        h = _stable_args_hash({"key": "value"})
        assert isinstance(h, str)

    def test_deterministic(self):
        a = _stable_args_hash({"b": 2, "a": 1})
        b = _stable_args_hash({"a": 1, "b": 2})
        assert a == b

    def test_different_args_different_hash(self):
        a = _stable_args_hash({"key": "a"})
        b = _stable_args_hash({"key": "b"})
        assert a != b


class TestToolPolicyEnforcerInit:
    def test_creates(self):
        enforcer = ToolPolicyEnforcer()
        assert enforcer is not None

    def test_policy_rules_start_empty(self):
        enforcer = ToolPolicyEnforcer()
        assert enforcer._policy_rules == {}

    def test_has_register_rule(self):
        assert hasattr(ToolPolicyEnforcer, "register_rule")

    def test_has_enforce(self):
        assert hasattr(ToolPolicyEnforcer, "enforce")


class TestToolPolicyEnforcerEnforce:
    def setup_method(self):
        self.enforcer = ToolPolicyEnforcer()

    def test_enforce_unknown_tool_returns_tuple(self):
        result = self.enforcer.enforce(
            tool_name="read_file",
            args={"path": "foo.py"},
        )
        assert isinstance(result, tuple)
        assert len(result) >= 2

    def test_enforce_default_outcome_pass(self):
        outcome, *_ = self.enforcer.enforce(
            tool_name="write_file",
            args={"path": "foo.py", "content": "hello"},
        )
        assert outcome == LawSlotOutcome.PASS

    def test_register_block_rule_enforces(self):
        self.enforcer.register_rule(
            "dangerous_tool",
            outcome=LawSlotOutcome.BLOCK,
            rationale="unsafe",
        )
        outcome, *_ = self.enforcer.enforce(
            tool_name="dangerous_tool",
            args={},
        )
        assert outcome == LawSlotOutcome.BLOCK
