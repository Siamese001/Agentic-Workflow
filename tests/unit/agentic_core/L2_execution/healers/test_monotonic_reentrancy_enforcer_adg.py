"""ADG-driven tests for L2_execution/healers/monotonic_reentrancy_enforcer.py — fan_in=0."""
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

_emit_records_execution_trace("p0", "evidence", "test_monotonic_reentrancy_enforcer_adg")
_emit_applies_guardrail("p0", "test_monotonic_reentrancy_enforcer_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_monotonic_reentrancy_enforcer_adg", "policy_binding")
_emit_snapshots_state("p0", "test_monotonic_reentrancy_enforcer_adg", "state_snapshot")
emit_replay_key("p0", "test_monotonic_reentrancy_enforcer_adg")
emit_determinism_digest("p0", "test_monotonic_reentrancy_enforcer_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.healers.monotonic_reentrancy_enforcer import (
    MonotonicReentrancyEnforcer,
    NonMonotonicRetryViolation,
)


class TestNonMonotonicRetryViolation:
    def test_is_exception(self):
        assert issubclass(NonMonotonicRetryViolation, Exception)


class TestMonotonicReentrancyEnforcer:
    def test_creates(self):
        enforcer = MonotonicReentrancyEnforcer()
        assert enforcer is not None

    def test_first_retry_is_one(self):
        enforcer = MonotonicReentrancyEnforcer()
        count = enforcer.get_and_increment_retry_count("trace-1")
        assert count == 1

    def test_second_retry_is_two(self):
        enforcer = MonotonicReentrancyEnforcer()
        enforcer.get_and_increment_retry_count("trace-1")
        count = enforcer.get_and_increment_retry_count("trace-1")
        assert count == 2

    def test_different_traces_independent(self):
        enforcer = MonotonicReentrancyEnforcer()
        enforcer.get_and_increment_retry_count("trace-a")
        count_b = enforcer.get_and_increment_retry_count("trace-b")
        assert count_b == 1
