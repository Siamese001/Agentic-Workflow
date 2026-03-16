"""
Phase 6 — Wave 1 Tests: read_only_retrieval_scope() + RetrievalMutationViolation.
"""

from __future__ import annotations

import pytest

from agentic_core.L4_state.enforcement.readonly_retrieval_scope import (
    RetrievalMutationViolation,
    assert_not_read_only,
    is_read_only_retrieval_active,
    read_only_retrieval_scope,
)
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

_emit_records_execution_trace("p0", "evidence", "test_readonly_scope")
_emit_applies_guardrail("p0", "test_readonly_scope", "p0_governance")
_emit_reads_policy_state("p0", "test_readonly_scope", "policy_binding")
_emit_snapshots_state("p0", "test_readonly_scope", "state_snapshot")
emit_replay_key("p0", "test_readonly_scope")
emit_determinism_digest("p0", "test_readonly_scope")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_readonly_scope", "execution_auth")
_emit_validates_capability("p2", "test_readonly_scope", "capability_check")
_emit_routes_to_capability("p2", "test_readonly_scope", "capability_route")
_emit_writes_via_uwg("p2", "test_readonly_scope", "uwg_write")
_emit_blocks_direct_write("p2", "test_readonly_scope", "direct_write_block")
_emit_records_tool_invocation("p2", "test_readonly_scope", "tool_invocation")
_emit_captures_execution_output("p2", "test_readonly_scope", "exec_output")
_emit_dispatches_agent("p3", "test_readonly_scope", "agent_dispatch")
_emit_coordinates_agents("p3", "test_readonly_scope", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_readonly_scope", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_readonly_scope", "healing_outcome")
_emit_escalates_failure("p3", "test_readonly_scope", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_readonly_scope", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_readonly_scope", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_readonly_scope", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_readonly_scope", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_readonly_scope", "eval_metric")
_emit_stores_embedding("p4", "test_readonly_scope", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_readonly_scope", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_readonly_scope", "exec_snapshot_link")

pytestmark = pytest.mark.unit_min_deps


class TestScopeActivation:
    def test_scope_inactive_by_default(self):
        assert is_read_only_retrieval_active() is False

    def test_scope_active_inside_context(self):
        with read_only_retrieval_scope():
            assert is_read_only_retrieval_active() is True

    def test_scope_inactive_after_context(self):
        with read_only_retrieval_scope():
            pass
        assert is_read_only_retrieval_active() is False

    def test_scope_restored_on_exception(self):
        with pytest.raises(RuntimeError):
            with read_only_retrieval_scope():
                raise RuntimeError("boom")
        assert is_read_only_retrieval_active() is False

    def test_nested_scope_stays_active_until_outermost_exits(self):
        with read_only_retrieval_scope():
            with read_only_retrieval_scope():
                assert is_read_only_retrieval_active() is True
            assert is_read_only_retrieval_active() is True
        assert is_read_only_retrieval_active() is False


class TestMutationBlockedInsideReadOnlyScope:
    def test_mutation_blocked_inside_read_only_scope(self):
        """
        Core Wave 1 guarantee: assert_not_read_only() raises inside scope.
        """
        with read_only_retrieval_scope():
            with pytest.raises(RetrievalMutationViolation) as exc_info:
                assert_not_read_only("redis.setex")
        assert "RETRIEVAL_MUTATION_BLOCKED" in str(exc_info.value)

    def test_mutation_blocked_includes_operation_detail(self):
        with read_only_retrieval_scope():
            with pytest.raises(RetrievalMutationViolation) as exc_info:
                assert_not_read_only("pinecone.upsert")
        assert "pinecone.upsert" in str(exc_info.value)

    def test_mutation_blocked_redis_setex(self):
        with read_only_retrieval_scope():
            with pytest.raises(RetrievalMutationViolation) as exc_info:
                assert_not_read_only("redis.setex")
        assert exc_info.value.code == "RETRIEVAL_MUTATION_BLOCKED"

    def test_mutation_blocked_pinecone_upsert(self):
        with read_only_retrieval_scope():
            with pytest.raises(RetrievalMutationViolation) as exc_info:
                assert_not_read_only("pinecone.upsert")
        assert exc_info.value.code == "RETRIEVAL_MUTATION_BLOCKED"

    def test_mutation_blocked_file_write(self):
        with read_only_retrieval_scope():
            with pytest.raises(RetrievalMutationViolation):
                assert_not_read_only("file.write")

    def test_violation_carries_code_substring(self):
        """Negative test: violation message contains code substring."""
        with read_only_retrieval_scope():
            try:
                assert_not_read_only("redis.set")
                pytest.fail("Expected RetrievalMutationViolation")
            except RetrievalMutationViolation as exc:  # guardian: allow-silent-swallower
                assert "RETRIEVAL_MUTATION_BLOCKED" in str(exc)
                assert exc.code == "RETRIEVAL_MUTATION_BLOCKED"

    def test_violation_detail_preserved(self):
        with read_only_retrieval_scope():
            try:
                assert_not_read_only("pinecone.upsert")
            except RetrievalMutationViolation as exc:  # guardian: allow-silent-swallower
                assert exc.detail == "pinecone.upsert"


class TestMutationAllowedOutsideReadOnlyScope:
    def test_mutation_allowed_outside_read_only_scope(self):
        """
        Core Wave 1 guarantee: assert_not_read_only() is a no-op outside scope.
        """
        assert_not_read_only("redis.setex")  # must not raise

    def test_mutation_allowed_after_scope_exits(self):
        with read_only_retrieval_scope():
            pass
        assert_not_read_only("pinecone.upsert")  # must not raise

    def test_mutation_allowed_with_empty_operation(self):
        assert_not_read_only("")  # must not raise

    def test_mutation_allowed_with_no_operation(self):
        assert_not_read_only()  # must not raise


class TestRetrievalMutationViolation:
    def test_violation_is_exception(self):
        exc = RetrievalMutationViolation("test detail")
        assert isinstance(exc, Exception)

    def test_violation_code_constant(self):
        assert RetrievalMutationViolation.code == "RETRIEVAL_MUTATION_BLOCKED"

    def test_violation_detail_stored(self):
        exc = RetrievalMutationViolation("my detail")
        assert exc.detail == "my detail"

    def test_violation_empty_detail(self):
        exc = RetrievalMutationViolation()
        assert exc.detail == ""
        assert "RETRIEVAL_MUTATION_BLOCKED" in str(exc)
