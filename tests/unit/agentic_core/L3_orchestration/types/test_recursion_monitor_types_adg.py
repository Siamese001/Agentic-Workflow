"""ADG contract tests for L3_orchestration/types/recursion_monitor_types.py."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_recursion_monitor_types_adg")
_emit_applies_guardrail("p0", "test_recursion_monitor_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_recursion_monitor_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_recursion_monitor_types_adg", "state_snapshot")
emit_replay_key("p0", "test_recursion_monitor_types_adg")
emit_determinism_digest("p0", "test_recursion_monitor_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_recursion_monitor_types_adg", "execution_auth")
_emit_validates_capability("p2", "test_recursion_monitor_types_adg", "capability_check")
_emit_routes_to_capability("p2", "test_recursion_monitor_types_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_recursion_monitor_types_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_recursion_monitor_types_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_recursion_monitor_types_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_recursion_monitor_types_adg", "exec_output")
_emit_dispatches_agent("p3", "test_recursion_monitor_types_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_recursion_monitor_types_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_recursion_monitor_types_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_recursion_monitor_types_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_recursion_monitor_types_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_recursion_monitor_types_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_recursion_monitor_types_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_recursion_monitor_types_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_recursion_monitor_types_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_recursion_monitor_types_adg", "eval_metric")
_emit_stores_embedding("p4", "test_recursion_monitor_types_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_recursion_monitor_types_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_recursion_monitor_types_adg", "exec_snapshot_link")
pytestmark = pytest.mark.unit
from agentic_core.L3_orchestration.types.recursion_monitor_types import (
    Alert,
    AlertSeverity,
    HealthStatus,
    RecursionMonitor,
)


class TestHealthStatus:
    def test_is_str_enum(self):
        import enum; assert issubclass(HealthStatus, str); assert issubclass(HealthStatus, enum.Enum)
    def test_has_healthy(self): assert HealthStatus.HEALTHY == "healthy"
    def test_has_critical(self): assert HealthStatus.CRITICAL == "critical"

class TestAlertSeverity:
    def test_is_str_enum(self):
        assert issubclass(AlertSeverity, str)
    def test_has_warning(self): assert AlertSeverity.WARNING == "warning"

class TestAlert:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(Alert)
    def test_creates(self):
        a = Alert(severity=AlertSeverity.INFO, message="ok", timestamp="2026-01-01", source="test")
        assert a.severity == AlertSeverity.INFO
        assert a.acknowledged is False

class TestRecursionMonitor:
    def test_creates(self):
        m = RecursionMonitor()
        assert m is not None
    def test_initial_circuit_closed(self):
        m = RecursionMonitor()
        assert m._circuit_open is False
    def test_record_spawn_success(self):
        m = RecursionMonitor()
        m.record_spawn(success=True, depth=2, duration_ms=10.0, memory_bytes=1024, cache_hit=True)
        assert m._consecutive_failures == 0
