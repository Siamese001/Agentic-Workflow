"""Unit tests for system_learning.enforcement.authority_invariants.

Covers:
  - EXECUTE mode => raises AuthorityViolation
  - ACTIVATE mode => raises AuthorityViolation
  - WRITE to audit surface => raises AuthorityViolation
  - Known audit-write operations => raises AuthorityViolation
  - READ from audit surface => no exception
  - Side-channel activation operations => raises AuthorityViolation
  - Direct ACTIVATE mode in no-side-channel guard => raises AuthorityViolation
"""

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

_emit_authorize_and_execute("p2", "test_authority_invariants", "execution_auth")
_emit_validates_capability("p2", "test_authority_invariants", "capability_check")
_emit_routes_to_capability("p2", "test_authority_invariants", "capability_route")
_emit_writes_via_uwg("p2", "test_authority_invariants", "uwg_write")
_emit_blocks_direct_write("p2", "test_authority_invariants", "direct_write_block")
_emit_records_tool_invocation("p2", "test_authority_invariants", "tool_invocation")
_emit_captures_execution_output("p2", "test_authority_invariants", "exec_output")
_emit_dispatches_agent("p3", "test_authority_invariants", "agent_dispatch")
_emit_coordinates_agents("p3", "test_authority_invariants", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_authority_invariants", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_authority_invariants", "healing_outcome")
_emit_escalates_failure("p3", "test_authority_invariants", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_authority_invariants", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_authority_invariants", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_authority_invariants", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_authority_invariants", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_authority_invariants", "eval_metric")
_emit_stores_embedding("p4", "test_authority_invariants", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_authority_invariants", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_authority_invariants", "exec_snapshot_link")
from system_learning.enforcement.authority_invariants import (
    AuthorityContext,
    AuthorityViolation,
    assert_no_side_channel_activation,
    assert_read_only_audit_access,
    assert_zero_execution_authority,
)

_emit_records_execution_trace("p0", "evidence", "test_authority_invariants")
_emit_applies_guardrail("p0", "test_authority_invariants", "p0_governance")
_emit_reads_policy_state("p0", "test_authority_invariants", "policy_binding")
_emit_snapshots_state("p0", "test_authority_invariants", "state_snapshot")
emit_replay_key("p0", "test_authority_invariants")
emit_determinism_digest("p0", "test_authority_invariants")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit_min_deps


# =============================================================================
# assert_zero_execution_authority
# =============================================================================


class TestAssertZeroExecutionAuthority:
    def test_execute_mode_raises(self):
        ctx = AuthorityContext(
            caller_layer="system_learning.test",
            operation="run_agent",
            target="l2_execution",
            mode="EXECUTE",
        )
        with pytest.raises(AuthorityViolation) as exc_info:
            assert_zero_execution_authority(ctx)
        assert "ZERO_EXECUTION_AUTHORITY" in str(exc_info.value)
        assert "EXECUTE" in str(exc_info.value)

    def test_activate_mode_raises(self):
        ctx = AuthorityContext(
            caller_layer="system_learning.test",
            operation="activate_package",
            target="l4_versioned_store",
            mode="ACTIVATE",
        )
        with pytest.raises(AuthorityViolation) as exc_info:
            assert_zero_execution_authority(ctx)
        assert "ZERO_EXECUTION_AUTHORITY" in str(exc_info.value)
        assert "ACTIVATE" in str(exc_info.value)

    def test_read_mode_allowed(self):
        ctx = AuthorityContext(
            caller_layer="system_learning.test",
            operation="read_audit_slice",
            target="l4_audit",
            mode="READ",
        )
        # Must not raise
        assert_zero_execution_authority(ctx)

    def test_write_mode_allowed_by_this_guard(self):
        """WRITE is permitted by zero-execution guard (audit guard handles write restrictions)."""
        ctx = AuthorityContext(
            caller_layer="system_learning.test",
            operation="write_change_package",
            target="l4_versioned_store",
            mode="WRITE",
        )
        # Must not raise — WRITE to versioned store is permitted
        assert_zero_execution_authority(ctx)

    def test_violation_message_contains_caller(self):
        ctx = AuthorityContext(
            caller_layer="system_learning.engines.rca",
            operation="execute_work_contract",
            target="l2_execution",
            mode="EXECUTE",
        )
        with pytest.raises(AuthorityViolation) as exc_info:
            assert_zero_execution_authority(ctx)
        assert "system_learning.engines.rca" in str(exc_info.value)

    def test_violation_message_contains_operation(self):
        ctx = AuthorityContext(
            caller_layer="system_learning.test",
            operation="execute_work_contract",
            target="l2_execution",
            mode="EXECUTE",
        )
        with pytest.raises(AuthorityViolation) as exc_info:
            assert_zero_execution_authority(ctx)
        assert "execute_work_contract" in str(exc_info.value)


# =============================================================================
# assert_read_only_audit_access
# =============================================================================


class TestAssertReadOnlyAuditAccess:
    def test_write_audit_operation_raises(self):
        ctx = AuthorityContext(
            caller_layer="system_learning.test",
            operation="write_audit",
            target="l4_audit",
            mode="WRITE",
        )
        with pytest.raises(AuthorityViolation) as exc_info:
            assert_read_only_audit_access(ctx)
        assert "AUDIT_WRITE_FORBIDDEN" in str(exc_info.value)

    def test_append_audit_operation_raises(self):
        ctx = AuthorityContext(
            caller_layer="system_learning.test",
            operation="append_audit",
            target="l4_audit",
            mode="WRITE",
        )
        with pytest.raises(AuthorityViolation) as exc_info:
            assert_read_only_audit_access(ctx)
        assert "AUDIT_WRITE_FORBIDDEN" in str(exc_info.value)

    def test_delete_audit_operation_raises(self):
        ctx = AuthorityContext(
            caller_layer="system_learning.test",
            operation="delete_audit",
            target="l4_audit",
            mode="WRITE",
        )
        with pytest.raises(AuthorityViolation) as exc_info:
            assert_read_only_audit_access(ctx)
        assert "AUDIT_WRITE_FORBIDDEN" in str(exc_info.value)

    def test_write_mode_to_audit_target_raises(self):
        ctx = AuthorityContext(
            caller_layer="system_learning.test",
            operation="some_operation",
            target="l4_audit_log",
            mode="WRITE",
        )
        with pytest.raises(AuthorityViolation) as exc_info:
            assert_read_only_audit_access(ctx)
        assert "AUDIT_SURFACE_NON_READ" in str(exc_info.value)

    def test_read_from_audit_allowed(self):
        ctx = AuthorityContext(
            caller_layer="system_learning.test",
            operation="read_audit_slice",
            target="l4_audit",
            mode="READ",
        )
        # Must not raise
        assert_read_only_audit_access(ctx)

    def test_write_to_non_audit_target_allowed(self):
        """Writing to non-audit targets (e.g., versioned store) is not blocked by this guard."""
        ctx = AuthorityContext(
            caller_layer="system_learning.test",
            operation="write_change_package",
            target="l4_versioned_store",
            mode="WRITE",
        )
        # Must not raise — this guard only restricts audit surfaces
        assert_read_only_audit_access(ctx)


# =============================================================================
# assert_no_side_channel_activation
# =============================================================================


class TestAssertNoSideChannelActivation:
    def test_update_activation_pointer_raises(self):
        ctx = AuthorityContext(
            caller_layer="system_learning.test",
            operation="update_activation_pointer",
            target="l4_versioned_store",
            mode="WRITE",
        )
        with pytest.raises(AuthorityViolation) as exc_info:
            assert_no_side_channel_activation(ctx)
        assert "SIDE_CHANNEL_ACTIVATION_FORBIDDEN" in str(exc_info.value)

    def test_set_active_version_raises(self):
        ctx = AuthorityContext(
            caller_layer="system_learning.test",
            operation="set_active_version",
            target="l4_versioned_store",
            mode="WRITE",
        )
        with pytest.raises(AuthorityViolation) as exc_info:
            assert_no_side_channel_activation(ctx)
        assert "SIDE_CHANNEL_ACTIVATION_FORBIDDEN" in str(exc_info.value)

    def test_activate_change_package_raises(self):
        ctx = AuthorityContext(
            caller_layer="system_learning.test",
            operation="activate_change_package",
            target="l4_versioned_store",
            mode="WRITE",
        )
        with pytest.raises(AuthorityViolation) as exc_info:
            assert_no_side_channel_activation(ctx)
        assert "SIDE_CHANNEL_ACTIVATION_FORBIDDEN" in str(exc_info.value)

    def test_activate_mode_raises(self):
        ctx = AuthorityContext(
            caller_layer="system_learning.test",
            operation="some_operation",
            target="l4_versioned_store",
            mode="ACTIVATE",
        )
        with pytest.raises(AuthorityViolation) as exc_info:
            assert_no_side_channel_activation(ctx)
        assert "DIRECT_ACTIVATE_FORBIDDEN" in str(exc_info.value)

    def test_write_change_package_allowed(self):
        """Writing a ChangePackage to versioned store is permitted (Stage A of 2PC)."""
        ctx = AuthorityContext(
            caller_layer="system_learning.test",
            operation="write_change_package",
            target="l4_versioned_store",
            mode="WRITE",
        )
        # Must not raise
        assert_no_side_channel_activation(ctx)

    def test_read_allowed(self):
        ctx = AuthorityContext(
            caller_layer="system_learning.test",
            operation="get_change_package",
            target="l4_versioned_store",
            mode="READ",
        )
        # Must not raise
        assert_no_side_channel_activation(ctx)
