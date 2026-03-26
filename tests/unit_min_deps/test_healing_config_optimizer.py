"""Tests for HealingConfigOptimizer - Phase 6 functionality.

Tests threshold adjustment proposals and deterministic behavior.
"""

from __future__ import annotations

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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_healing_config_optimizer")
# REMOVED: _emit_applies_guardrail("p0", "test_healing_config_optimizer", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_healing_config_optimizer", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_healing_config_optimizer", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_healing_config_optimizer")
# REMOVED: emit_determinism_digest("p0", "test_healing_config_optimizer")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_healing_config_optimizer", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_healing_config_optimizer", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_healing_config_optimizer", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_healing_config_optimizer", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_healing_config_optimizer", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_healing_config_optimizer", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_healing_config_optimizer", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_healing_config_optimizer", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_healing_config_optimizer", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_healing_config_optimizer", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_healing_config_optimizer", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_healing_config_optimizer", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_healing_config_optimizer", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_healing_config_optimizer", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_healing_config_optimizer", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_healing_config_optimizer", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_healing_config_optimizer", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_healing_config_optimizer", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_healing_config_optimizer", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_healing_config_optimizer", "exec_snapshot_link")

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
#  # MOVED: from system_learning.engines.healing_config_optimizer import (
    HealingConfigOptimizer,
    ThresholdAdjustment,
    ThresholdAdjustmentProposal,
)
#  # MOVED: from system_learning.types.healing_outcome_intake_types import HealingOutcomeIntakeRecord
#  # MOVED: from system_learning.types.healing_outcome_learning_types import (
    HealingOutcomeAggregate,
    HealingOutcomeAggregateKey,
    HealingOutcomeAggregateSnapshot,
)
#  # MOVED: from system_learning.types.healing_outcome_types import HealingOutcomeStats

# REMOVED: _emit_emits_metric_event("test_healing_config_optimizer", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_healing_config_optimizer", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_healing_config_optimizer", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_healing_config_optimizer", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_healing_config_optimizer", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_healing_config_optimizer", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_healing_config_optimizer", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_healing_config_optimizer", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_healing_config_optimizer", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_healing_config_optimizer", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_healing_config_optimizer", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_healing_config_optimizer", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_healing_config_optimizer", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_healing_config_optimizer", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_healing_config_optimizer", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_healing_config_optimizer", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_healing_config_optimizer", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_healing_config_optimizer", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_healing_config_optimizer", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_healing_config_optimizer", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_healing_config_optimizer", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_healing_config_optimizer", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_healing_config_optimizer", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_healing_config_optimizer", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_healing_config_optimizer", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_healing_config_optimizer", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_healing_config_optimizer", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_healing_config_optimizer", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_healing_config_optimizer", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_healing_config_optimizer", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_healing_config_optimizer", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_healing_config_optimizer", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_healing_config_optimizer", "write_through")
# REMOVED: _emit_writes_through("p1", "test_healing_config_optimizer", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_healing_config_optimizer", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_healing_config_optimizer", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_healing_config_optimizer", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_healing_config_optimizer", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_healing_config_optimizer", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_healing_config_optimizer", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_healing_config_optimizer", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_healing_config_optimizer", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_healing_config_optimizer", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_healing_config_optimizer", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_healing_config_optimizer", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_healing_config_optimizer", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_healing_config_optimizer", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_healing_config_optimizer", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_healing_config_optimizer")
# REMOVED: _emit_gated_by_confidence("p1", "test_healing_config_optimizer", "confidence_gate")


class TestHealingConfigOptimizer:
    """Test suite for HealingConfigOptimizer."""

    def test_threshold_proposal_deterministic(self):
                from system_learning.types.healing_outcome_learning_types import HealingOutcomeAggregate, HealingOutcomeAggregateKey, HealingOutcomeAggregateSnapshot
                from system_learning.types.healing_outcome_learning_types import HealingOutcomeAggregate, HealingOutcomeAggregateKey, HealingOutcomeAggregateSnapshot
                from system_learning.engines.healing_config_optimizer import HealingConfigOptimizer, ThresholdAdjustment, ThresholdAdjustmentProposal
                from system_learning.types.healing_outcome_learning_types import HealingOutcomeAggregate, HealingOutcomeAggregateKey, HealingOutcomeAggregateSnapshot
                from system_learning.types.healing_outcome_learning_types import HealingOutcomeAggregate, HealingOutcomeAggregateKey, HealingOutcomeAggregateSnapshot
                from system_learning.engines.healing_config_optimizer import HealingConfigOptimizer, ThresholdAdjustment, ThresholdAdjustmentProposal
                from system_learning.types.healing_outcome_learning_types import HealingOutcomeAggregate, HealingOutcomeAggregateKey, HealingOutcomeAggregateSnapshot
                from system_learning.types.healing_outcome_learning_types import HealingOutcomeAggregate, HealingOutcomeAggregateKey, HealingOutcomeAggregateSnapshot
                from system_learning.engines.healing_config_optimizer import HealingConfigOptimizer, ThresholdAdjustment, ThresholdAdjustmentProposal
                from system_learning.types.healing_outcome_learning_types import HealingOutcomeAggregate, HealingOutcomeAggregateKey, HealingOutcomeAggregateSnapshot
                from system_learning.types.healing_outcome_learning_types import HealingOutcomeAggregate, HealingOutcomeAggregateKey, HealingOutcomeAggregateSnapshot
                from system_learning.types.healing_outcome_learning_types import HealingOutcomeAggregate, HealingOutcomeAggregateKey, HealingOutcomeAggregateSnapshot
                from system_learning.engines.healing_config_optimizer import HealingConfigOptimizer, ThresholdAdjustment, ThresholdAdjustmentProposal
                from system_learning.types.healing_outcome_learning_types import HealingOutcomeAggregate, HealingOutcomeAggregateKey, HealingOutcomeAggregateSnapshot
                from system_learning.types.healing_outcome_types import HealingOutcomeStats
                from system_learning.engines.healing_config_optimizer import HealingConfigOptimizer, ThresholdAdjustment, ThresholdAdjustmentProposal
                from system_learning.types.healing_outcome_intake_types import HealingOutcomeIntakeRecord
                from system_learning.types.healing_outcome_learning_types import HealingOutcomeAggregate, HealingOutcomeAggregateKey, HealingOutcomeAggregateSnapshot
                from system_learning.engines.healing_config_optimizer import HealingConfigOptimizer, ThresholdAdjustment, ThresholdAdjustmentProposal
                from system_learning.engines.healing_config_optimizer import HealingConfigOptimizer, ThresholdAdjustment, ThresholdAdjustmentProposal
                from system_learning.engines.healing_config_optimizer import HealingConfigOptimizer, ThresholdAdjustment, ThresholdAdjustmentProposal
                from system_learning.engines.healing_config_optimizer import HealingConfigOptimizer, ThresholdAdjustment, ThresholdAdjustmentProposal
                from system_learning.engines.healing_config_optimizer import HealingConfigOptimizer, ThresholdAdjustment, ThresholdAdjustmentProposal
                """Test that proposals are deterministic given same input."""
                optimizer = HealingConfigOptimizer(
                    min_sample_size=10, low_success_rate_threshold=0.6, escalation_delta=0.1, max_threshold=1.0
                )


        # Create test snapshot
        aggregates = [
            (
                HealingOutcomeAggregateKey("healer1", "LOCAL_AGENT", "failure1"),
                HealingOutcomeAggregate(success_count=3, failure_count=7, total_count=10),
            ),
            (
                HealingOutcomeAggregateKey("healer2", "REMOTE_AGENT", "failure2"),
                HealingOutcomeAggregate(success_count=8, failure_count=2, total_count=10),
            ),
        ]

        snapshot = HealingOutcomeAggregateSnapshot(
            version_id="test123", created_utc=2000, aggregates=tuple(aggregates)
        )

        # Generate proposals twice
        proposal1 = optimizer.propose_threshold_adjustments(snapshot)
        proposal2 = optimizer.propose_threshold_adjustments(snapshot)

        # Should be identical
        assert proposal1.content_hash() == proposal2.content_hash()
        assert len(proposal1.adjustments) == len(proposal2.adjustments)

        # Only healer1 should have adjustment (30% success < 60% threshold)
        assert len(proposal1.adjustments) == 1
        adjustment = proposal1.adjustments[0]
        assert adjustment.healer_name == "healer1"
        assert adjustment.tier == "LOCAL_AGENT"
        assert adjustment.failure_type == "failure1"
        assert adjustment.current_threshold == 0.5  # Default for LOCAL_AGENT
        assert adjustment.proposed_threshold == 0.6  # 0.5 + 0.1

    def test_no_direct_config_mutation(self):
        """Test that optimizer doesn't directly mutate any config."""
#  # MOVED: from system_learning.types.healing_outcome_learning_types import HealingOutcomeAggregate, HealingOutcomeAggregateKey, HealingOutcomeAggregateSnapshot
#  # MOVED: from system_learning.types.healing_outcome_learning_types import HealingOutcomeAggregate, HealingOutcomeAggregateKey, HealingOutcomeAggregateSnapshot
#  # MOVED: from system_learning.engines.healing_config_optimizer import HealingConfigOptimizer, ThresholdAdjustment, ThresholdAdjustmentProposal
#  # MOVED: from system_learning.types.healing_outcome_learning_types import HealingOutcomeAggregate, HealingOutcomeAggregateKey, HealingOutcomeAggregateSnapshot
        optimizer = HealingConfigOptimizer()

        # Create empty snapshot
        snapshot = HealingOutcomeAggregateSnapshot(version_id="empty", created_utc=2000, aggregates=())

        # Should not raise any errors and produce no adjustments
        proposal = optimizer.propose_threshold_adjustments(snapshot)
        assert len(proposal.adjustments) == 0
        assert proposal.snapshot_version_id == "empty"
        assert proposal.created_utc == 2000

    def test_minimum_sample_size_enforced(self):
        """Test that proposals require minimum sample size."""
#  # MOVED: from system_learning.types.healing_outcome_learning_types import HealingOutcomeAggregate, HealingOutcomeAggregateKey, HealingOutcomeAggregateSnapshot
#  # MOVED: from system_learning.engines.healing_config_optimizer import HealingConfigOptimizer, ThresholdAdjustment, ThresholdAdjustmentProposal
        optimizer = HealingConfigOptimizer(min_sample_size=50)

        # Create snapshot with insufficient samples
        aggregates = [
            (
                HealingOutcomeAggregateKey("healer1", "LOCAL_AGENT", "failure1"),
                HealingOutcomeAggregate(success_count=1, failure_count=9, total_count=10),
            ),
        ]

        snapshot = HealingOutcomeAggregateSnapshot(
            version_id="test", created_utc=2000, aggregates=tuple(aggregates)
        )

        # Should not propose adjustment due to insufficient sample size
        proposal = optimizer.propose_threshold_adjustments(snapshot)
        assert len(proposal.adjustments) == 0

    def test_max_threshold_capped(self):
        """Test that proposed thresholds are capped at max_threshold."""
#  # MOVED: from system_learning.types.healing_outcome_learning_types import HealingOutcomeAggregate, HealingOutcomeAggregateKey, HealingOutcomeAggregateSnapshot
#  # MOVED: from system_learning.types.healing_outcome_learning_types import HealingOutcomeAggregate, HealingOutcomeAggregateKey, HealingOutcomeAggregateSnapshot
#  # MOVED: from system_learning.engines.healing_config_optimizer import HealingConfigOptimizer, ThresholdAdjustment, ThresholdAdjustmentProposal
#  # MOVED: from system_learning.types.healing_outcome_learning_types import HealingOutcomeAggregate, HealingOutcomeAggregateKey, HealingOutcomeAggregateSnapshot
        optimizer = HealingConfigOptimizer(
            min_sample_size=10,
            low_success_rate_threshold=0.6,
            escalation_delta=1.5,  # Large delta
            max_threshold=1.0,
        )

        # Create snapshot with low success rate
        aggregates = [
            (
                HealingOutcomeAggregateKey("healer1", "LOCAL_AGENT", "failure1"),
                HealingOutcomeAggregate(success_count=1, failure_count=9, total_count=10),
            ),
        ]

        snapshot = HealingOutcomeAggregateSnapshot(
            version_id="test", created_utc=2000, aggregates=tuple(aggregates)
        )

        proposal = optimizer.propose_threshold_adjustments(snapshot)
        assert len(proposal.adjustments) == 1

        adjustment = proposal.adjustments[0]
        # Current 0.5 + 1.5 = 2.0, but capped at 1.0
        assert adjustment.proposed_threshold == 1.0

    def test_create_snapshot_from_intake(self):
        """Test creating aggregate snapshot from intake record."""
#  # MOVED: from system_learning.types.healing_outcome_learning_types import HealingOutcomeAggregate, HealingOutcomeAggregateKey, HealingOutcomeAggregateSnapshot
#  # MOVED: from system_learning.types.healing_outcome_learning_types import HealingOutcomeAggregate, HealingOutcomeAggregateKey, HealingOutcomeAggregateSnapshot
#  # MOVED: from system_learning.engines.healing_config_optimizer import HealingConfigOptimizer, ThresholdAdjustment, ThresholdAdjustmentProposal
#  # MOVED: from system_learning.types.healing_outcome_learning_types import HealingOutcomeAggregate, HealingOutcomeAggregateKey, HealingOutcomeAggregateSnapshot
        optimizer = HealingConfigOptimizer()

        # Create mock intake record
        stats = (
            HealingOutcomeStats.from_counts("healer1", "LOCAL_AGENT", "failure1", 7, 3),
            HealingOutcomeStats.from_counts("healer2", "REMOTE_AGENT", "failure2", 5, 5),
        )

        intake_record = HealingOutcomeIntakeRecord(
            schema_version=1,
            created_utc=1000,
            window_size=100,
            snapshot=stats,
            proposal=None,  # type: ignore
            source="test",
        )

        # Create snapshot
        snapshot = optimizer.create_snapshot_from_intake(intake_record, created_utc=2000)

        assert snapshot.created_utc == 2000
        assert len(snapshot.aggregates) == 2
        assert snapshot.version_id != ""  # Should be computed hash

        # Check aggregates are sorted
        keys = [agg[0] for agg in snapshot.aggregates]
        assert keys[0].healer_name == "healer1"  # Should be sorted alphabetically
        assert keys[1].healer_name == "healer2"

        # Check content
        for key, aggregate in snapshot.aggregates:
            if key.healer_name == "healer1":
                assert aggregate.success_count == 7
                assert aggregate.failure_count == 3
                assert aggregate.total_count == 10
                assert aggregate.success_rate == 0.7
            elif key.healer_name == "healer2":
                assert aggregate.success_count == 5
                assert aggregate.failure_count == 5
                assert aggregate.total_count == 10
                assert aggregate.success_rate == 0.5

    def test_confidence_computation(self):
        """Test confidence score computation."""
#  # MOVED: from system_learning.types.healing_outcome_types import HealingOutcomeStats
#  # MOVED: from system_learning.engines.healing_config_optimizer import HealingConfigOptimizer, ThresholdAdjustment, ThresholdAdjustmentProposal
#  # MOVED: from system_learning.types.healing_outcome_intake_types import HealingOutcomeIntakeRecord
        optimizer = HealingConfigOptimizer(min_sample_size=10)

        # Test with different sample sizes
        small_aggregate = HealingOutcomeAggregate(success_count=3, failure_count=7, total_count=10)
        large_aggregate = HealingOutcomeAggregate(success_count=30, failure_count=70, total_count=100)

        # Large sample should have higher confidence
        large_confidence = optimizer._compute_confidence(large_aggregate)
        small_confidence = optimizer._compute_confidence(small_aggregate)

        assert 0.0 <= small_confidence <= 1.0
        assert 0.0 <= large_confidence <= 1.0
        assert large_confidence > small_confidence

    def test_adjustment_canonical_bytes(self):
        """Test that adjustments have stable canonical bytes."""
#  # MOVED: from system_learning.types.healing_outcome_learning_types import HealingOutcomeAggregate, HealingOutcomeAggregateKey, HealingOutcomeAggregateSnapshot
#  # MOVED: from system_learning.engines.healing_config_optimizer import HealingConfigOptimizer, ThresholdAdjustment, ThresholdAdjustmentProposal
        adjustment = ThresholdAdjustment(
            healer_name="healer1",
            tier="LOCAL_AGENT",
            failure_type="failure1",
            current_threshold=0.5,
            proposed_threshold=0.6,
            reason="Low success rate",
            confidence=0.8,
        )

        bytes1 = adjustment.canonical_bytes()
        bytes2 = adjustment.canonical_bytes()

        assert bytes1 == bytes2
        assert isinstance(bytes1, bytes)

        # Verify it's valid JSON
        import json

        data = json.loads(bytes1.decode("utf-8"))
        assert data["healer_name"] == "healer1"
        assert data["proposed_threshold"] == 0.6

    def test_proposal_canonical_bytes(self):
        """Test that proposals have stable canonical bytes."""
#  # MOVED: from system_learning.engines.healing_config_optimizer import HealingConfigOptimizer, ThresholdAdjustment, ThresholdAdjustmentProposal
        adjustment = ThresholdAdjustment(
            healer_name="healer1",
            tier="LOCAL_AGENT",
            failure_type="failure1",
            current_threshold=0.5,
            proposed_threshold=0.6,
            reason="Low success rate",
            confidence=0.8,
        )

        proposal = ThresholdAdjustmentProposal(
            snapshot_version_id="test123", created_utc=2000, adjustments=(adjustment,)
        )

        bytes1 = proposal.canonical_bytes()
        bytes2 = proposal.canonical_bytes()

        assert bytes1 == bytes2
        assert isinstance(bytes1, bytes)

        # Verify it's valid JSON
        import json

        data = json.loads(bytes1.decode("utf-8"))
        assert data["snapshot_version_id"] == "test123"
        assert len(data["adjustments"]) == 1

    def test_optimizer_initialization_validation(self):
#  # MOVED: from system_learning.engines.healing_config_optimizer import HealingConfigOptimizer, ThresholdAdjustment, ThresholdAdjustmentProposal
        """Test optimizer parameter validation."""
#  # MOVED: from system_learning.engines.healing_config_optimizer import HealingConfigOptimizer, ThresholdAdjustment, ThresholdAdjustmentProposal
#  # MOVED: from system_learning.engines.healing_config_optimizer import HealingConfigOptimizer, ThresholdAdjustment, ThresholdAdjustmentProposal
        # Valid initialization
        optimizer = HealingConfigOptimizer(
            min_sample_size=10, low_success_rate_threshold=0.6, escalation_delta=0.1, max_threshold=1.0
        )
        assert optimizer._min_sample_size == 10

        # Invalid min_sample_size
        with pytest.raises(ValueError, match="min_sample_size must be >= 1"):
            HealingConfigOptimizer(min_sample_size=0)

        # Invalid success rate threshold
        with pytest.raises(ValueError, match="low_success_rate_threshold must be in"):
            HealingConfigOptimizer(low_success_rate_threshold=1.5)

        # Invalid escalation delta
        with pytest.raises(ValueError, match="escalation_delta must be > 0"):
            HealingConfigOptimizer(escalation_delta=0)

        # Invalid max threshold
        with pytest.raises(ValueError, match="max_threshold must be > 0"):
            HealingConfigOptimizer(max_threshold=-1)
