"""ADG-driven tests for L5_safety/enforcement/AdapterBase.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_adapter_base_adg")
_emit_applies_guardrail("p0", "test_adapter_base_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_adapter_base_adg", "policy_binding")
_emit_snapshots_state("p0", "test_adapter_base_adg", "state_snapshot")
emit_replay_key("p0", "test_adapter_base_adg")
emit_determinism_digest("p0", "test_adapter_base_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_adapter_base_adg", "execution_auth")
_emit_validates_capability("p2", "test_adapter_base_adg", "capability_check")
_emit_routes_to_capability("p2", "test_adapter_base_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_adapter_base_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_adapter_base_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_adapter_base_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_adapter_base_adg", "exec_output")
_emit_dispatches_agent("p3", "test_adapter_base_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_adapter_base_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_adapter_base_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_adapter_base_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_adapter_base_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_adapter_base_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_adapter_base_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_adapter_base_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_adapter_base_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_adapter_base_adg", "eval_metric")
_emit_stores_embedding("p4", "test_adapter_base_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_adapter_base_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_adapter_base_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.enforcement.AdapterBase import AdapterContext, AdapterResult


class TestAdapterContext:
    def test_creates_with_request_id(self):
        ctx = AdapterContext(request_id="req-001")
        assert ctx.request_id == "req-001"

    def test_risk_level_default_medium(self):
        ctx = AdapterContext(request_id="r")
        assert ctx.risk_level == "medium"

    def test_bypass_validation_default_false(self):
        ctx = AdapterContext(request_id="r")
        assert ctx.bypass_validation is False

    def test_metadata_default_empty(self):
        ctx = AdapterContext(request_id="r")
        assert ctx.metadata == {}

    def test_timestamp_set(self):
        ctx = AdapterContext(request_id="r")
        assert ctx.timestamp is not None


class TestAdapterResult:
    def test_creates_success(self):
        r = AdapterResult(success=True, data={"key": "val"})
        assert r.success is True
        assert r.data == {"key": "val"}

    def test_creates_failure(self):
        r = AdapterResult(success=False, error="something went wrong")
        assert r.success is False
        assert r.error == "something went wrong"

    def test_data_default_none(self):
        r = AdapterResult(success=True)
        assert r.data is None

    def test_error_default_none(self):
        r = AdapterResult(success=True)
        assert r.error is None
