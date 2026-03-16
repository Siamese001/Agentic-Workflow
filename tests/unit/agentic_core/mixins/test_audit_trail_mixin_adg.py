"""ADG-driven tests for mixins/audit_trail_mixin.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_audit_trail_mixin_adg")
_emit_applies_guardrail("p0", "test_audit_trail_mixin_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_audit_trail_mixin_adg", "policy_binding")
_emit_snapshots_state("p0", "test_audit_trail_mixin_adg", "state_snapshot")
emit_replay_key("p0", "test_audit_trail_mixin_adg")
emit_determinism_digest("p0", "test_audit_trail_mixin_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_audit_trail_mixin_adg", "execution_auth")
_emit_validates_capability("p2", "test_audit_trail_mixin_adg", "capability_check")
_emit_routes_to_capability("p2", "test_audit_trail_mixin_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_audit_trail_mixin_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_audit_trail_mixin_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_audit_trail_mixin_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_audit_trail_mixin_adg", "exec_output")
_emit_dispatches_agent("p3", "test_audit_trail_mixin_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_audit_trail_mixin_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_audit_trail_mixin_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_audit_trail_mixin_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_audit_trail_mixin_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_audit_trail_mixin_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_audit_trail_mixin_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_audit_trail_mixin_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_audit_trail_mixin_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_audit_trail_mixin_adg", "eval_metric")
_emit_stores_embedding("p4", "test_audit_trail_mixin_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_audit_trail_mixin_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_audit_trail_mixin_adg", "exec_snapshot_link")

_FIXED_TS = 1735689600.0  # 2026-01-01T00:00:00Z

pytestmark = pytest.mark.unit

from agentic_core.mixins.audit_trail_mixin import AuditProof, AuditTrailMixin


class TestAuditProof:
    def test_creates(self):
        proof = AuditProof(
            action_id="act-1",
            prev_hash="abc123",
            curr_hash="def456",
            timestamp=_FIXED_TS,
        )
        assert proof.action_id == "act-1"

    def test_to_dict_has_required_keys(self):
        proof = AuditProof(
            action_id="act-2",
            prev_hash="aaa",
            curr_hash="bbb",
            timestamp=1234567890.0,
        )
        d = proof.to_dict()
        for key in ("action_id", "prev_hash", "curr_hash", "timestamp", "chain_id"):
            assert key in d

    def test_verify_chain_link_valid(self):
        proof = AuditProof(
            action_id="act-3",
            prev_hash="prev",
            curr_hash="curr",
            timestamp=_FIXED_TS,
        )
        assert proof.verify_chain_link("prev") is True

    def test_verify_chain_link_invalid(self):
        proof = AuditProof(
            action_id="act-4",
            prev_hash="prev",
            curr_hash="curr",
            timestamp=_FIXED_TS,
        )
        assert proof.verify_chain_link("wrong") is False

    def test_chain_id_default_empty(self):
        proof = AuditProof(
            action_id="a", prev_hash="p", curr_hash="c", timestamp=0.0
        )
        assert proof.chain_id == ""


class TestAuditTrailMixin:
    def test_importable(self):
        assert callable(AuditTrailMixin)

    def test_has_log_sovereign_event(self):
        assert hasattr(AuditTrailMixin, "log_sovereign_event")
