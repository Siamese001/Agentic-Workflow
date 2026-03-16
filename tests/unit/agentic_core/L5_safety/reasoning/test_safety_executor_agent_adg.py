"""ADG-driven tests for L5_safety/reasoning/SafetyExecutorAgent.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_safety_executor_agent_adg")
_emit_applies_guardrail("p0", "test_safety_executor_agent_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_safety_executor_agent_adg", "policy_binding")
_emit_snapshots_state("p0", "test_safety_executor_agent_adg", "state_snapshot")
emit_replay_key("p0", "test_safety_executor_agent_adg")
emit_determinism_digest("p0", "test_safety_executor_agent_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.reasoning.SafetyExecutorAgent import (
    BlockReason,
    ExecutionStatus,
    SafetyExecutorAgent,
)


class TestExecutionStatus:
    def test_allowed_member(self):
        assert hasattr(ExecutionStatus, "ALLOWED")

    def test_blocked_member(self):
        assert hasattr(ExecutionStatus, "BLOCKED")

    def test_warned_member(self):
        assert hasattr(ExecutionStatus, "WARNED")

    def test_failed_member(self):
        assert hasattr(ExecutionStatus, "FAILED")


class TestBlockReason:
    def test_safety_violation_member(self):
        assert hasattr(BlockReason, "SAFETY_VIOLATION")

    def test_integrity_failure_member(self):
        assert hasattr(BlockReason, "INTEGRITY_FAILURE")

    def test_permission_denied_member(self):
        assert hasattr(BlockReason, "PERMISSION_DENIED")


class TestSafetyExecutorAgent:
    def test_creates(self):
        agent = SafetyExecutorAgent()
        assert agent is not None

    def test_has_heal_repository(self):
        assert hasattr(SafetyExecutorAgent, "heal_repository")
