"""Unit tests for system_learning.engines.l4_audit_reader.

Covers:
  - Valid read returns expected bytes
  - Window invalid => ValueError
  - AuditStore protocol has no write methods
  - Authority guard is called (assert_read_only_audit_access invoked)
"""

from unittest.mock import MagicMock, patch

import pytest

#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_authorize_and_execute("p2", "test_l4_audit_reader", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_l4_audit_reader", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_l4_audit_reader", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_l4_audit_reader", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_l4_audit_reader", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_l4_audit_reader", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_l4_audit_reader", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_l4_audit_reader", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_l4_audit_reader", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_l4_audit_reader", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_l4_audit_reader", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_l4_audit_reader", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_l4_audit_reader", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_l4_audit_reader", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_l4_audit_reader", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_l4_audit_reader", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_l4_audit_reader", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_l4_audit_reader", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_l4_audit_reader", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_l4_audit_reader", "exec_snapshot_link")
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)
#  # MOVED: from system_learning.enforcement.authority_invariants import AuthorityViolation
#  # MOVED: from system_learning.engines.l4_audit_reader import AuditStore, pull_audit_data

# REMOVED: _emit_emits_metric_event("test_l4_audit_reader", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_l4_audit_reader", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_l4_audit_reader", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_l4_audit_reader", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_l4_audit_reader", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_l4_audit_reader", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_l4_audit_reader", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_l4_audit_reader", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_l4_audit_reader", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_l4_audit_reader", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_l4_audit_reader", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_l4_audit_reader", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_l4_audit_reader", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_l4_audit_reader", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_l4_audit_reader", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_l4_audit_reader", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_l4_audit_reader", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_l4_audit_reader", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_l4_audit_reader", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_l4_audit_reader", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_l4_audit_reader", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_l4_audit_reader", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_l4_audit_reader", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_l4_audit_reader", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_l4_audit_reader", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_l4_audit_reader", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_l4_audit_reader", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_l4_audit_reader", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_l4_audit_reader")
# REMOVED: _emit_applies_guardrail("p0", "test_l4_audit_reader", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_l4_audit_reader", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_l4_audit_reader", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_l4_audit_reader", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_l4_audit_reader", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_l4_audit_reader", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_l4_audit_reader", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_l4_audit_reader", "write_through")
# REMOVED: _emit_writes_through("p1", "test_l4_audit_reader", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_l4_audit_reader", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_l4_audit_reader", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_l4_audit_reader", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_l4_audit_reader", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_l4_audit_reader", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_l4_audit_reader", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_l4_audit_reader", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_l4_audit_reader", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_l4_audit_reader", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_l4_audit_reader", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_l4_audit_reader", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_l4_audit_reader", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_l4_audit_reader", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_l4_audit_reader", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_l4_audit_reader")
# REMOVED: _emit_gated_by_confidence("p1", "test_l4_audit_reader", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_l4_audit_reader")
# REMOVED: emit_determinism_digest("p0", "test_l4_audit_reader")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.unit_min_deps


# =============================================================================
# Fake in-memory AuditStore for tests
# =============================================================================


class FakeAuditStore:
    """Pure in-memory fake implementing AuditStore protocol."""

    def __init__(self, data: bytes = b"") -> None:
        self._data = data

    def read_audit_slice(self, window_start_utc: int, window_end_utc: int) -> bytes:
        return self._data


# =============================================================================
# Protocol conformance
# =============================================================================


class TestAuditStoreProtocol:
    def test_fake_store_satisfies_protocol(self):
                from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
                from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
                from system_learning.enforcement.authority_invariants import AuthorityViolation
                from system_learning.engines.l4_audit_reader import AuditStore, pull_audit_data
                store = FakeAuditStore(b"test")
                assert isinstance(store, AuditStore)

        assert isinstance(store, AuditStore)

    def test_protocol_has_no_write_methods(self):
        """AuditStore protocol must not expose any write/delete/mutate methods."""
        forbidden = {
            "write_audit_slice",
            "append_audit_slice",
            "delete_audit_slice",
            "mutate_audit",
            "overwrite_audit",
            "patch_audit",
        }
        protocol_attrs = set(dir(AuditStore))
        intersection = forbidden & protocol_attrs
        assert not intersection, f"AuditStore protocol exposes forbidden write methods: {intersection}"

    def test_fake_store_has_no_write_methods(self):
        """FakeAuditStore must not expose write methods."""
        store = FakeAuditStore()
        forbidden = {
            "write_audit_slice",
            "append_audit_slice",
            "delete_audit_slice",
        }
        store_attrs = set(dir(store))
        intersection = forbidden & store_attrs
        assert not intersection, f"FakeAuditStore exposes forbidden write methods: {intersection}"


# =============================================================================
# pull_audit_data — valid reads
# =============================================================================


class TestPullAuditDataValid:
    def test_returns_expected_bytes(self):
        expected = b"audit-data-slice"
        store = FakeAuditStore(expected)
        result = pull_audit_data(store, 1_700_000_000, 1_700_003_600)
        assert result == expected

    def test_returns_empty_bytes_when_store_empty(self):
        store = FakeAuditStore(b"")
        result = pull_audit_data(store, 1_700_000_000, 1_700_003_600)
        assert result == b""

    def test_returns_bytes_unmodified(self):
        """pull_audit_data must not mutate the returned bytes."""
        raw = b"\x00\x01\x02\x03\xff\xfe"
        store = FakeAuditStore(raw)
        result = pull_audit_data(store, 1_700_000_000, 1_700_003_600)
        assert result == raw
        assert result is not None

    def test_delegates_window_to_store(self):
        """pull_audit_data must pass window parameters to store unchanged."""
        mock_store = MagicMock(spec=FakeAuditStore)
        mock_store.read_audit_slice.return_value = b"data"
        pull_audit_data(mock_store, 1_700_000_000, 1_700_003_600)
        mock_store.read_audit_slice.assert_called_once_with(1_700_000_000, 1_700_003_600)


# =============================================================================
# pull_audit_data — invalid window
# =============================================================================


class TestPullAuditDataInvalidWindow:
    def test_start_equal_to_end_raises(self):
        store = FakeAuditStore(b"data")
        with pytest.raises(ValueError, match="INVALID_AUDIT_WINDOW"):
            pull_audit_data(store, 1_700_000_000, 1_700_000_000)

    def test_start_greater_than_end_raises(self):
        store = FakeAuditStore(b"data")
        with pytest.raises(ValueError, match="INVALID_AUDIT_WINDOW"):
            pull_audit_data(store, 1_700_003_600, 1_700_000_000)

    def test_store_not_called_on_invalid_window(self):
    """Test store_not_called_on_invalid_window runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute store_not_called_on_invalid_window
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
    """Test assert_read_only_audit_access_is_called runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute assert_read_only_audit_access_is_called
    """Test assert_zero_execution_authority_is_called runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute assert_zero_execution_authority_is_called
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions

        with patch(
            "system_learning.engines.l4_audit_reader.assert_read_only_audit_access",
            side_effect=capture,
        ):
            pull_audit_data(store, 1_700_000_000, 1_700_003_600)

        assert len(captured_ctx) == 1
        assert captured_ctx[0].mode == "READ"

    def test_authority_context_targets_l4_audit(self):
        """The AuthorityContext must target 'l4_audit'."""
        store = FakeAuditStore(b"data")
        captured_ctx = []

        def capture(ctx):
            captured_ctx.append(ctx)

        with patch(
            "system_learning.engines.l4_audit_reader.assert_read_only_audit_access",
            side_effect=capture,
        ):
            pull_audit_data(store, 1_700_000_000, 1_700_003_600)

        assert "audit" in captured_ctx[0].target.lower()

    def test_authority_violation_propagates(self):
        """If a guard raises AuthorityViolation, it must propagate to caller."""
        store = FakeAuditStore(b"data")
        with patch(
            "system_learning.engines.l4_audit_reader.assert_zero_execution_authority",
            side_effect=AuthorityViolation("TEST_VIOLATION"),
        ):
            with pytest.raises(AuthorityViolation, match="TEST_VIOLATION"):
                pull_audit_data(store, 1_700_000_000, 1_700_003_600)
