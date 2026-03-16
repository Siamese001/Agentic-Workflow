"""ADG-driven tests for runtime/execution_trace.py — fan_in=1."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "test_execution_trace_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_execution_trace_adg", "policy_binding")
_emit_snapshots_state("p0", "test_execution_trace_adg", "state_snapshot")
emit_replay_key("p0", "test_execution_trace_adg")
emit_determinism_digest("p0", "test_execution_trace_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.runtime.execution_trace import ExecutionTrace, ExecutionTraceManager


class TestExecutionTrace:
    def test_creates(self):
        trace = ExecutionTrace(
            trace_id="trace-abc",
            plan_hash="phash",
            policy_hash="pohash",
            determinism_digest="ddig",
            hierarchy_hash="hhash",
            metadata={},
        )
        assert trace.trace_id == "trace-abc"

    def test_is_frozen(self):
        trace = ExecutionTrace(
            trace_id="t",
            plan_hash="p",
            policy_hash="po",
            determinism_digest="d",
            hierarchy_hash="h",
            metadata={},
        )
        with pytest.raises(Exception):
            trace.trace_id = "modified"


class TestExecutionTraceManager:
    def test_creates(self):
        manager = ExecutionTraceManager()
        assert manager is not None

    def test_start_trace_returns_str(self):
        manager = ExecutionTraceManager()
        trace_id = manager.start_trace(
            plan_hash="p",
            policy_hash="po",
            hierarchy_hash="h",
        )
        assert isinstance(trace_id, str)
        assert len(trace_id) > 0

    def test_has_active_trace_after_start(self):
        manager = ExecutionTraceManager()
        manager.start_trace(plan_hash="p", policy_hash="po", hierarchy_hash="h")
        assert manager._active_trace is not None
