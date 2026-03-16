"""ADG-driven tests for runtime/execution_bound_token.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_execution_bound_token_adg")
_emit_applies_guardrail("p0", "test_execution_bound_token_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_execution_bound_token_adg", "policy_binding")
_emit_snapshots_state("p0", "test_execution_bound_token_adg", "state_snapshot")
emit_replay_key("p0", "test_execution_bound_token_adg")
emit_determinism_digest("p0", "test_execution_bound_token_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_execution_bound_token_adg", "execution_auth")
_emit_validates_capability("p2", "test_execution_bound_token_adg", "capability_check")
_emit_routes_to_capability("p2", "test_execution_bound_token_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_execution_bound_token_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_execution_bound_token_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_execution_bound_token_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_execution_bound_token_adg", "exec_output")
_emit_dispatches_agent("p3", "test_execution_bound_token_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_execution_bound_token_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_execution_bound_token_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_execution_bound_token_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_execution_bound_token_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_execution_bound_token_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_execution_bound_token_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_execution_bound_token_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_execution_bound_token_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_execution_bound_token_adg", "eval_metric")
_emit_stores_embedding("p4", "test_execution_bound_token_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_execution_bound_token_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_execution_bound_token_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.runtime.execution_bound_token import CapabilityType, ExecutionBoundToken


class TestCapabilityType:
    def test_read_only_value(self):
        assert CapabilityType.READ_ONLY.value == "read_only"

    def test_write_state_value(self):
        assert CapabilityType.WRITE_STATE.value == "write_state"

    def test_mutate_config_value(self):
        assert CapabilityType.MUTATE_CONFIG.value == "mutate_config"

    def test_all_types(self):
        for name in ("READ_ONLY", "WRITE_STATE", "MUTATE_CONFIG", "ACTIVATE_LEARNING"):
            assert hasattr(CapabilityType, name)


class TestExecutionBoundToken:
    def test_creates(self):
        token = ExecutionBoundToken(
            token_id="tok-1",
            capability_type=CapabilityType.READ_ONLY,
            caller_context="AgentA",
            target_context="AgentB",
            execution_trace_id="trace-1",
            policy_hash="phash",
            determinism_digest="ddig",
            hierarchy_hash="hhash",
            signature_hash="sig",
            authority_hash="auth",
        )
        assert token.token_id == "tok-1"
        assert token.capability_type == CapabilityType.READ_ONLY

    def test_is_frozen(self):
        token = ExecutionBoundToken(
            token_id="t2",
            capability_type=CapabilityType.WRITE_STATE,
            caller_context="A",
            target_context="B",
            execution_trace_id="tr",
            policy_hash="p",
            determinism_digest="d",
            hierarchy_hash="h",
            signature_hash="s",
            authority_hash="a",
        )
        with pytest.raises(Exception):
            token.token_id = "modified"

    def test_metadata_default_empty(self):
        token = ExecutionBoundToken(
            token_id="t3",
            capability_type=CapabilityType.READ_ONLY,
            caller_context="X",
            target_context="Y",
            execution_trace_id="tr",
            policy_hash="p",
            determinism_digest="d",
            hierarchy_hash="h",
            signature_hash="s",
            authority_hash="a",
        )
        assert token.metadata == {}
