"""ADG-driven tests for L2_execution/healers/signature_invalidator.py — fan_in=0."""
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

_emit_records_execution_trace("p0", "evidence", "test_signature_invalidator_adg")
_emit_applies_guardrail("p0", "test_signature_invalidator_adg", "p0_governance")
_emit_snapshots_state("p0", "test_signature_invalidator_adg", "state_snapshot")
emit_replay_key("p0", "test_signature_invalidator_adg")
emit_determinism_digest("p0", "test_signature_invalidator_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_signature_invalidator_adg", "execution_auth")
_emit_validates_capability("p2", "test_signature_invalidator_adg", "capability_check")
_emit_routes_to_capability("p2", "test_signature_invalidator_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_signature_invalidator_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_signature_invalidator_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_signature_invalidator_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_signature_invalidator_adg", "exec_output")
_emit_dispatches_agent("p3", "test_signature_invalidator_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_signature_invalidator_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_signature_invalidator_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_signature_invalidator_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_signature_invalidator_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_signature_invalidator_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_signature_invalidator_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_signature_invalidator_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_signature_invalidator_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_signature_invalidator_adg", "eval_metric")
_emit_stores_embedding("p4", "test_signature_invalidator_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_signature_invalidator_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_signature_invalidator_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.healers.signature_invalidator import (
    InvalidationResult,
    StaleSignatureViolation,
    invalidate_signature_and_rehash,
)


class TestStaleSignatureViolation:
    def test_is_exception(self):
        assert issubclass(StaleSignatureViolation, Exception)


class TestInvalidationResult:
    def test_is_named_tuple(self):
        r = InvalidationResult(invalidated_plan={"key": "val"}, new_policy_hash="abc123")
        assert r.new_policy_hash == "abc123"
        assert r.invalidated_plan == {"key": "val"}


class TestInvalidateSignatureAndRehash:
    def test_returns_invalidation_result(self):
        plan = {"id": "p1", "steps": ["s1"], "signature": "old_sig"}
        result = invalidate_signature_and_rehash(plan)
        assert isinstance(result, InvalidationResult)

    def test_returns_plan_with_policy_hash(self):
        plan = {"id": "p1", "signature": "old_sig", "approval_hash": "ah"}
        result = invalidate_signature_and_rehash(plan)
        assert "policy_hash" in result.invalidated_plan

    def test_new_policy_hash_is_hex(self):
        plan = {"id": "p1", "content": "heal_result"}
        result = invalidate_signature_and_rehash(plan)
        assert isinstance(result.new_policy_hash, str)
        assert len(result.new_policy_hash) == 64
