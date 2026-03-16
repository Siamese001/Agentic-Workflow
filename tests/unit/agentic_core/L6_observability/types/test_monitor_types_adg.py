"""ADG-driven tests for L6_observability/types/monitor_types.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_monitor_types_adg")
_emit_applies_guardrail("p0", "test_monitor_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_monitor_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_monitor_types_adg", "state_snapshot")
emit_replay_key("p0", "test_monitor_types_adg")
emit_determinism_digest("p0", "test_monitor_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L6_observability.types.monitor_types import (
    AggregatedMetrics,
    ExecutionMetrics,
)


class TestExecutionMetrics:
    def test_creates(self):
        m = ExecutionMetrics(
            agent_name="TestAgent",
            category="reasoning",
            strategy_type="heal",
            execution_time_ms=42.5,
            success=True,
        )
        assert m.agent_name == "TestAgent"
        assert m.success is True

    def test_execution_time_stored(self):
        m = ExecutionMetrics(
            agent_name="A",
            category="c",
            strategy_type="s",
            execution_time_ms=100.0,
            success=False,
        )
        assert m.execution_time_ms == pytest.approx(100.0)

    def test_metadata_default_empty(self):
        m = ExecutionMetrics(
            agent_name="A",
            category="c",
            strategy_type="s",
            execution_time_ms=0.0,
            success=True,
        )
        assert m.metadata == {}


class TestAggregatedMetrics:
    def test_creates_with_defaults(self):
        a = AggregatedMetrics()
        assert a.total_executions == 0
        assert a.successful_executions == 0

    def test_min_starts_at_inf(self):
        a = AggregatedMetrics()
        assert a.min_execution_time_ms == float("inf")

    def test_executions_by_category_default_empty(self):
        a = AggregatedMetrics()
        assert a.executions_by_category == {}
