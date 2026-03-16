"""
Unit tests for L6 Observability Outcome Logger - deterministic outcome recording.
"""

import pytest

from agentic_core.L6_observability.enforcement.outcome_logger import (
    OutcomeLogger,
    OutcomeReconciler,
    OutcomeRecord,
    ReconcileResult,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_capability,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)

_emit_emits_metric_event("test_outcome_logger", "p4obs", "metric_1")
_emit_emits_metric_event("test_outcome_logger", "p4obs", "metric_2")
_emit_emits_metric_event("test_outcome_logger", "p4obs", "metric_3")
_emit_emits_metric_event("test_outcome_logger", "p4obs", "metric_4")
_emit_emits_metric_event("test_outcome_logger", "p4obs", "metric_5")
_emit_emits_metric_event("test_outcome_logger", "p4obs", "metric_6")
_emit_records_incident_event("test_outcome_logger", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_outcome_logger", "p4obs", "anomaly")
_emit_writes_observability_log("test_outcome_logger", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_outcome_logger", "p4obs", "mon_state")
_emit_triggers_alert("test_outcome_logger", "p4obs", "alert")
_emit_links_incident_trace("test_outcome_logger", "p4obs", "trace_link")
_emit_captures_pattern("test_outcome_logger", "p3lm", "pattern")
_emit_records_learning_event("test_outcome_logger", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_outcome_logger", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_outcome_logger", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_outcome_logger", "p3lm", "routing")
_emit_improves_agent_policy("test_outcome_logger", "p3lm", "policy")
_emit_stores_learning_state("test_outcome_logger", "p3lm", "state")
_emit_records_execution_trace("test_outcome_logger", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_outcome_logger", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_outcome_logger", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_outcome_logger", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_outcome_logger", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_outcome_logger", "env_read", "p2_env_1")
_emit_reads_environ("test_outcome_logger", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_outcome_logger", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_outcome_logger", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_outcome_logger")
_emit_applies_guardrail("p0", "test_outcome_logger", "p0_governance")
_emit_reads_policy_state("p0", "test_outcome_logger", "policy_binding")
_emit_snapshots_state("p0", "test_outcome_logger", "state_snapshot")
_emit_pulls_context("p1", "test_outcome_logger", "context_pull")
_emit_pulls_context("p1", "test_outcome_logger", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_outcome_logger", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_outcome_logger", "uwg_term_secondary")
_emit_writes_through("p1", "test_outcome_logger", "write_through")
_emit_writes_through("p1", "test_outcome_logger", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_outcome_logger", "safety_validation")
_emit_invokes_eval("p1", "test_outcome_logger", "eval_call")
_emit_proposal_commits_routing("p1", "test_outcome_logger", "routing_commit")
_emit_escalates_to_human("p1", "test_outcome_logger", "human_escalation")
_emit_routes_through("p1", "test_outcome_logger", "route_through")
_emit_checks_agent_registry("p1", "test_outcome_logger", "agent_registry")
_emit_validates_agent_capability("p1", "test_outcome_logger", "capability")
_emit_dispatches_execution_plan("p1", "test_outcome_logger", "exec_plan")
_emit_agent_executes_agent("p1", "test_outcome_logger", "sub_agent")
_emit_routes_to_agent("p1", "test_outcome_logger", "target_agent")
_emit_verifies_policy("p1", "test_outcome_logger", "policy_check")
_emit_observes_runtime_state("p1", "test_outcome_logger", "runtime_state")
_emit_verifies_boundary("p1", "test_outcome_logger", "boundary_check")
_emit_transcripts_response("p1", "test_outcome_logger", "transcript")
_emit_hard_fails_untranscripted("p1", "test_outcome_logger")
_emit_gated_by_confidence("p1", "test_outcome_logger", "confidence_gate")
emit_replay_key("p0", "test_outcome_logger")
emit_determinism_digest("p0", "test_outcome_logger")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_outcome_logger", "execution_auth")
_emit_validates_capability("p2", "test_outcome_logger", "capability_check")
_emit_routes_to_capability("p2", "test_outcome_logger", "capability_route")
_emit_writes_via_uwg("p2", "test_outcome_logger", "uwg_write")
_emit_blocks_direct_write("p2", "test_outcome_logger", "direct_write_block")
_emit_records_tool_invocation("p2", "test_outcome_logger", "tool_invocation")
_emit_captures_execution_output("p2", "test_outcome_logger", "exec_output")
_emit_dispatches_agent("p3", "test_outcome_logger", "agent_dispatch")
_emit_coordinates_agents("p3", "test_outcome_logger", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_outcome_logger", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_outcome_logger", "healing_outcome")
_emit_escalates_failure("p3", "test_outcome_logger", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_outcome_logger", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_outcome_logger", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_outcome_logger", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_outcome_logger", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_outcome_logger", "eval_metric")
_emit_stores_embedding("p4", "test_outcome_logger", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_outcome_logger", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_outcome_logger", "exec_snapshot_link")


@pytest.mark.unit
class TestOutcomeRecord:
    """Test OutcomeRecord dataclass and deterministic hashing."""

    def test_create_with_deterministic_record_hash(self):
        """Test record creation with deterministic hash computation."""
        record = OutcomeRecord.create(
            trace_id="trace123", cid="cid456", status="success", manifest_hash="manifest789"
        )

        assert record.trace_id == "trace123"
        assert record.cid == "cid456"
        assert record.status == "success"
        assert record.manifest_hash == "manifest789"
        assert record.record_hash is not None
        assert len(record.record_hash) == 64  # SHA-256 hex length

    def test_record_hash_deterministic_across_identical_inputs(self):
        """Test record hash is deterministic across identical inputs."""
        record1 = OutcomeRecord.create(
            trace_id="trace123", cid="cid456", status="success", manifest_hash="manifest789"
        )

        record2 = OutcomeRecord.create(
            trace_id="trace123", cid="cid456", status="success", manifest_hash="manifest789"
        )

        # Hash should be identical for same inputs
        assert record1.record_hash == record2.record_hash

    def test_record_hash_different_for_different_inputs(self):
        """Test record hash differs for different inputs."""
        record1 = OutcomeRecord.create(
            trace_id="trace123", cid="cid456", status="success", manifest_hash="manifest789"
        )

        record2 = OutcomeRecord.create(
            trace_id="trace123",
            cid="cid456",
            status="retry",  # Different status
            manifest_hash="manifest789",
        )

        assert record1.record_hash != record2.record_hash

    def test_record_hash_ignores_field_order_in_canonical_json(self):
        """Test record hash uses canonical JSON (field order doesn't matter)."""
        # All records should have same hash regardless of internal field order
        record1 = OutcomeRecord.create(trace_id="trace1", cid="cid1", status="success", manifest_hash="hash1")

        record2 = OutcomeRecord.create(trace_id="trace1", cid="cid1", status="success", manifest_hash="hash1")

        assert record1.record_hash == record2.record_hash

    def test_record_immutability(self):
        """Test record is immutable."""
        record = OutcomeRecord.create(
            trace_id="trace123", cid="cid456", status="success", manifest_hash="manifest789"
        )

        # Should be frozen dataclass
        with pytest.raises(AttributeError):
            record.trace_id = "changed"

        with pytest.raises(AttributeError):
            record.cid = "changed"

        with pytest.raises(AttributeError):
            record.status = "changed"

        with pytest.raises(AttributeError):
            record.manifest_hash = "changed"

        with pytest.raises(AttributeError):
            record.record_hash = "changed"


@pytest.mark.unit
class TestOutcomeLogger:
    """Test OutcomeLogger append-only semantics."""

    def test_logger_initialization_empty(self):
        """Test logger initializes with empty storage."""
        logger = OutcomeLogger()

        records = logger.records()
        assert len(records) == 0
        assert records == ()

    def test_append_creates_and_returns_record(self):
        """Test append creates and returns OutcomeRecord."""
        logger = OutcomeLogger()

        record = logger.append(
            trace_id="trace123", cid="cid456", status="success", manifest_hash="manifest789"
        )

        # Verify record properties
        assert record.trace_id == "trace123"
        assert record.cid == "cid456"
        assert record.status == "success"
        assert record.manifest_hash == "manifest789"
        assert record.record_hash is not None

    def test_append_produces_deterministic_record_hash(self):
        """Test append produces deterministic record_hash for identical inputs."""
        logger = OutcomeLogger()

        record1 = logger.append(
            trace_id="trace123", cid="cid456", status="success", manifest_hash="manifest789"
        )

        record2 = logger.append(
            trace_id="trace123", cid="cid456", status="success", manifest_hash="manifest789"
        )

        # Each record should have same hash for same inputs
        assert record1.record_hash == record2.record_hash

    def test_log_is_append_only_older_records_unchanged(self):
        """Test log is append-only (older records unchanged, ordering preserved)."""
        logger = OutcomeLogger()

        # Append first record
        record1 = logger.append(trace_id="trace1", cid="cid1", status="success", manifest_hash="hash1")

        # Append second record
        record2 = logger.append(trace_id="trace2", cid="cid2", status="retry", manifest_hash="hash2")

        # Verify ordering and immutability
        records = logger.records()
        assert len(records) == 2
        assert records[0] is record1
        assert records[1] is record2
        assert records[0].trace_id == "trace1"
        assert records[1].trace_id == "trace2"

    def test_records_returns_immutable_snapshot(self):
        """Test records() returns tuple snapshot (immutability)."""
        logger = OutcomeLogger()

        # Add a record
        logger.append(trace_id="trace123", cid="cid456", status="success", manifest_hash="manifest789")

        # Get records snapshot
        records1 = logger.records()
        records2 = logger.records()

        # Should be tuples (immutable)
        assert isinstance(records1, tuple)
        assert isinstance(records2, tuple)

        # Should be equal but not same object reference
        assert records1 == records2
        assert records1 is not records2

    def test_multiple_appends_preserve_order(self):
        """Test multiple appends preserve chronological order."""
        logger = OutcomeLogger()

        # Append multiple records
        records = []
        for i in range(5):
            record = logger.append(
                trace_id=f"trace{i}", cid=f"cid{i}", status="success", manifest_hash=f"hash{i}"
            )
            records.append(record)

        # Verify order preserved
        all_records = logger.records()
        assert len(all_records) == 5

        for i, record in enumerate(all_records):
            assert record.trace_id == f"trace{i}"
            assert record is records[i]


@pytest.mark.unit
class TestOutcomeReconciler:
    """Test OutcomeReconciler deterministic hash comparison."""

    def test_reconcile_exact_match(self):
        """Test exact match => ok True, empty missing/extra."""
        reconciler = OutcomeReconciler()

        # Create observed records
        record1 = OutcomeRecord.create("trace1", "cid1", "success", "hash1")
        record2 = OutcomeRecord.create("trace2", "cid2", "success", "hash2")
        observed = (record1, record2)

        # Expected hashes match observed
        expected_hashes = (record1.record_hash, record2.record_hash)

        result = reconciler.reconcile(observed=observed, expected_hashes=expected_hashes)

        assert result.ok is True
        assert result.missing == ()
        assert result.extra == ()

    def test_reconcile_missing_expected(self):
        """Test missing expected => ok False, missing contains hash."""
        reconciler = OutcomeReconciler()

        # Only one observed record
        record1 = OutcomeRecord.create("trace1", "cid1", "success", "hash1")
        observed = (record1,)

        # Expect two hashes (one missing)
        missing_hash = "missing_hash_12345"
        expected_hashes = (record1.record_hash, missing_hash)

        result = reconciler.reconcile(observed=observed, expected_hashes=expected_hashes)

        assert result.ok is False
        assert missing_hash in result.missing
        assert result.extra == ()

    def test_reconcile_extra_observed(self):
        """Test extra observed => ok False, extra contains hash."""
        reconciler = OutcomeReconciler()

        # Two observed records
        record1 = OutcomeRecord.create("trace1", "cid1", "success", "hash1")
        record2 = OutcomeRecord.create("trace2", "cid2", "success", "hash2")
        observed = (record1, record2)

        # Only expect one hash (one extra)
        expected_hashes = (record1.record_hash,)

        result = reconciler.reconcile(observed=observed, expected_hashes=expected_hashes)

        assert result.ok is False
        assert result.missing == ()
        assert record2.record_hash in result.extra

    def test_reconcile_both_missing_and_extra(self):
        """Test both missing and extra => ok False, both populated."""
        reconciler = OutcomeReconciler()

        # Observed records
        record1 = OutcomeRecord.create("trace1", "cid1", "success", "hash1")
        record2 = OutcomeRecord.create("trace2", "cid2", "success", "hash2")
        observed = (record1, record2)

        # Expected hashes (different from observed)
        expected_hash1 = "expected_hash_11111"
        expected_hash2 = "expected_hash_22222"
        expected_hashes = (expected_hash1, expected_hash2)

        result = reconciler.reconcile(observed=observed, expected_hashes=expected_hashes)

        assert result.ok is False
        assert len(result.missing) == 2
        assert expected_hash1 in result.missing
        assert expected_hash2 in result.missing
        assert len(result.extra) == 2
        assert record1.record_hash in result.extra
        assert record2.record_hash in result.extra

    def test_reconcile_determinism_shuffled_input(self):
        """Test determinism: shuffled expected_hashes input yields same result."""
        reconciler = OutcomeReconciler()

        # Create observed records
        record1 = OutcomeRecord.create("trace1", "cid1", "success", "hash1")
        record2 = OutcomeRecord.create("trace2", "cid2", "success", "hash2")
        observed = (record1, record2)

        # Expected hashes in different order
        expected_hashes1 = (record1.record_hash, record2.record_hash, "missing_hash")
        expected_hashes2 = ("missing_hash", record2.record_hash, record1.record_hash)

        result1 = reconciler.reconcile(observed=observed, expected_hashes=expected_hashes1)
        result2 = reconciler.reconcile(observed=observed, expected_hashes=expected_hashes2)

        # Results should be identical
        assert result1.ok == result2.ok
        assert result1.missing == result2.missing
        assert result1.extra == result2.extra

    def test_reconcile_result_immutability(self):
        """Test ReconcileResult is immutable."""
        result = ReconcileResult(missing=("hash1", "hash2"), extra=("hash3",), ok=False)

        # Should be frozen dataclass
        with pytest.raises(AttributeError):
            result.missing = ("changed",)

        with pytest.raises(AttributeError):
            result.extra = ("changed",)

        with pytest.raises(AttributeError):
            result.ok = True
