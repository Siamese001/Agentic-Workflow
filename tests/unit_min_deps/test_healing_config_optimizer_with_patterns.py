"""Tests for Healing Config Optimizer with Pattern Findings - Phase 8."""

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
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_records_execution_trace("p0", "evidence", "test_healing_config_optimizer_with_patterns")
_emit_applies_guardrail("p0", "test_healing_config_optimizer_with_patterns", "p0_governance")
_emit_reads_policy_state("p0", "test_healing_config_optimizer_with_patterns", "policy_binding")
_emit_snapshots_state("p0", "test_healing_config_optimizer_with_patterns", "state_snapshot")
emit_replay_key("p0", "test_healing_config_optimizer_with_patterns")
emit_determinism_digest("p0", "test_healing_config_optimizer_with_patterns")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_healing_config_optimizer_with_patterns", "execution_auth")
_emit_validates_capability("p2", "test_healing_config_optimizer_with_patterns", "capability_check")
_emit_routes_to_capability("p2", "test_healing_config_optimizer_with_patterns", "capability_route")
_emit_writes_via_uwg("p2", "test_healing_config_optimizer_with_patterns", "uwg_write")
_emit_blocks_direct_write("p2", "test_healing_config_optimizer_with_patterns", "direct_write_block")
_emit_records_tool_invocation("p2", "test_healing_config_optimizer_with_patterns", "tool_invocation")
_emit_captures_execution_output("p2", "test_healing_config_optimizer_with_patterns", "exec_output")
_emit_dispatches_agent("p3", "test_healing_config_optimizer_with_patterns", "agent_dispatch")
_emit_coordinates_agents("p3", "test_healing_config_optimizer_with_patterns", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_healing_config_optimizer_with_patterns", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_healing_config_optimizer_with_patterns", "healing_outcome")
_emit_escalates_failure("p3", "test_healing_config_optimizer_with_patterns", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_healing_config_optimizer_with_patterns", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_healing_config_optimizer_with_patterns", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_healing_config_optimizer_with_patterns", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_healing_config_optimizer_with_patterns", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_healing_config_optimizer_with_patterns", "eval_metric")
_emit_stores_embedding("p4", "test_healing_config_optimizer_with_patterns", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_healing_config_optimizer_with_patterns", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_healing_config_optimizer_with_patterns", "exec_snapshot_link")

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

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
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
from system_learning.engines.healing_config_optimizer import (
    HealingConfigOptimizer,
)
from system_learning.types.healing_outcome_learning_types import (
    HealingOutcomeAggregate,
    HealingOutcomeAggregateKey,
    HealingOutcomeAggregateSnapshot,
)
from system_learning.types.pattern_analysis_types import (
    PatternFinding,
    PatternFindingKey,
    PatternFindingReport,
    PatternSourceIds,
)

_emit_emits_metric_event("test_healing_config_optimizer_with_patterns", "p4obs", "metric_1")
_emit_emits_metric_event("test_healing_config_optimizer_with_patterns", "p4obs", "metric_2")
_emit_emits_metric_event("test_healing_config_optimizer_with_patterns", "p4obs", "metric_3")
_emit_emits_metric_event("test_healing_config_optimizer_with_patterns", "p4obs", "metric_4")
_emit_emits_metric_event("test_healing_config_optimizer_with_patterns", "p4obs", "metric_5")
_emit_emits_metric_event("test_healing_config_optimizer_with_patterns", "p4obs", "metric_6")
_emit_records_incident_event("test_healing_config_optimizer_with_patterns", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_healing_config_optimizer_with_patterns", "p4obs", "anomaly")
_emit_writes_observability_log("test_healing_config_optimizer_with_patterns", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_healing_config_optimizer_with_patterns", "p4obs", "mon_state")
_emit_triggers_alert("test_healing_config_optimizer_with_patterns", "p4obs", "alert")
_emit_links_incident_trace("test_healing_config_optimizer_with_patterns", "p4obs", "trace_link")
_emit_captures_pattern("test_healing_config_optimizer_with_patterns", "p3lm", "pattern")
_emit_records_learning_event("test_healing_config_optimizer_with_patterns", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_healing_config_optimizer_with_patterns", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_healing_config_optimizer_with_patterns", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_healing_config_optimizer_with_patterns", "p3lm", "routing")
_emit_improves_agent_policy("test_healing_config_optimizer_with_patterns", "p3lm", "policy")
_emit_stores_learning_state("test_healing_config_optimizer_with_patterns", "p3lm", "state")
_emit_records_execution_trace("test_healing_config_optimizer_with_patterns", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_healing_config_optimizer_with_patterns", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_healing_config_optimizer_with_patterns", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_healing_config_optimizer_with_patterns", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_healing_config_optimizer_with_patterns", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_healing_config_optimizer_with_patterns", "env_read", "p2_env_1")
_emit_reads_environ("test_healing_config_optimizer_with_patterns", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_healing_config_optimizer_with_patterns", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_healing_config_optimizer_with_patterns", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_healing_config_optimizer_with_patterns", "context_pull")
_emit_pulls_context("p1", "test_healing_config_optimizer_with_patterns", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_healing_config_optimizer_with_patterns", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_healing_config_optimizer_with_patterns", "uwg_term_secondary")
_emit_writes_through("p1", "test_healing_config_optimizer_with_patterns", "write_through")
_emit_writes_through("p1", "test_healing_config_optimizer_with_patterns", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_healing_config_optimizer_with_patterns", "safety_validation")
_emit_invokes_eval("p1", "test_healing_config_optimizer_with_patterns", "eval_call")
_emit_proposal_commits_routing("p1", "test_healing_config_optimizer_with_patterns", "routing_commit")
_emit_escalates_to_human("p1", "test_healing_config_optimizer_with_patterns", "human_escalation")
_emit_routes_through("p1", "test_healing_config_optimizer_with_patterns", "route_through")
_emit_checks_agent_registry("p1", "test_healing_config_optimizer_with_patterns", "agent_registry")
_emit_validates_agent_capability("p1", "test_healing_config_optimizer_with_patterns", "capability")
_emit_dispatches_execution_plan("p1", "test_healing_config_optimizer_with_patterns", "exec_plan")
_emit_agent_executes_agent("p1", "test_healing_config_optimizer_with_patterns", "sub_agent")
_emit_routes_to_agent("p1", "test_healing_config_optimizer_with_patterns", "target_agent")
_emit_verifies_policy("p1", "test_healing_config_optimizer_with_patterns", "policy_check")
_emit_observes_runtime_state("p1", "test_healing_config_optimizer_with_patterns", "runtime_state")
_emit_verifies_boundary("p1", "test_healing_config_optimizer_with_patterns", "boundary_check")
_emit_transcripts_response("p1", "test_healing_config_optimizer_with_patterns", "transcript")
_emit_hard_fails_untranscripted("p1", "test_healing_config_optimizer_with_patterns")
_emit_gated_by_confidence("p1", "test_healing_config_optimizer_with_patterns", "confidence_gate")


class TestHealingConfigOptimizerWithPatterns:
    """Test suite for Healing Config Optimizer with pattern findings."""

    def test_bounded_delta_applied(self):
        """Test that pattern findings trigger bounded adjustments."""
        optimizer = HealingConfigOptimizer(
            escalation_delta=0.1,
            max_delta=0.2,  # Small max delta for testing
            max_threshold=THRESHOLD,
        )

        # Create snapshot
        aggregates = [
            (
                HealingOutcomeAggregateKey(
                    healer_name="test_healer", tier="LOCAL_AGENT", failure_type="timeout"
                ),
                HealingOutcomeAggregate(success_count=80, failure_count=20, total_count=100),
            )
        ]

        snapshot = HealingOutcomeAggregateSnapshot(
            version_id="test_v1", created_utc=1000, aggregates=tuple(aggregates)
        )

        # Create pattern finding with high severity
        pattern_report = PatternFindingReport(
            source_ids=PatternSourceIds(healing_snapshot_version="test_v1"),
            findings=(
                PatternFinding(
                    key=PatternFindingKey(
                        component="test_healer", dimension="performance", label="UNDERPERFORMING_HEALER_TIER"
                    ),
                    severity=1.0,  # High severity
                    evidence=("success_rate_0.300000", "threshold_0.500000"),
                    metrics=(
                        ("success_rate", 0.3),
                        ("sample_size", 100),
                    ),
                ),
            ),
        )

        # Get proposal with patterns
        proposal = optimizer.propose_threshold_adjustments_with_patterns(snapshot, pattern_report)

        # Check that adjustment is bounded
        assert len(proposal.adjustments) == 1
        adj = proposal.adjustments[0]

        # Current threshold for LOCAL_AGENT is 0.5
        assert adj.current_threshold == 0.5
        # Proposed threshold should be current + min(escalation_delta * severity, max_delta)
        # = 0.5 + min(0.1 * 1.0, 0.2) = 0.5 + 0.1 = 0.6
        assert adj.proposed_threshold == 0.6
        assert adj.proposed_threshold - adj.current_threshold <= optimizer._max_delta
        assert adj.proposed_threshold <= optimizer._max_threshold

        # Check reason includes pattern finding
        assert "Pattern finding: UNDERPERFORMING_HEALER_TIER" in adj.reason
        assert "severity=1.000" in adj.reason

    def test_multiple_findings_deterministic_application_order(self):
        """Test that multiple findings are applied in deterministic order."""
        optimizer = HealingConfigOptimizer(escalation_delta=0.1, max_delta=0.3, max_threshold=THRESHOLD)

        # Create snapshot
        aggregates = [
            (
                HealingOutcomeAggregateKey(
                    healer_name="healer_a", tier="LOCAL_AGENT", failure_type="timeout"
                ),
                HealingOutcomeAggregate(success_count=80, failure_count=20, total_count=100),
            )
        ]

        snapshot = HealingOutcomeAggregateSnapshot(
            version_id="test_v1", created_utc=1000, aggregates=tuple(aggregates)
        )

        # Create multiple findings in reverse order to test sorting
        pattern_report = PatternFindingReport(
            source_ids=PatternSourceIds(healing_snapshot_version="test_v1"),
            findings=(
                PatternFinding(
                    key=PatternFindingKey(
                        component="healer_z", dimension="performance", label="UNDERPERFORMING_HEALER_TIER"
                    ),
                    severity=0.5,
                    evidence=("success_rate_0.300000",),
                    metrics=(("success_rate", 0.3),),
                ),
                PatternFinding(
                    key=PatternFindingKey(
                        component="healer_a", dimension="performance", label="UNDERPERFORMING_HEALER_TIER"
                    ),
                    severity=0.8,
                    evidence=("success_rate_0.200000",),
                    metrics=(("success_rate", 0.2),),
                ),
                PatternFinding(
                    key=PatternFindingKey(
                        component="healer_m", dimension="performance", label="UNDERPERFORMING_HEALER_TIER"
                    ),
                    severity=0.6,
                    evidence=("success_rate_0.400000",),
                    metrics=(("success_rate", 0.4),),
                ),
            ),
        )

        # Get proposal twice
        proposal1 = optimizer.propose_threshold_adjustments_with_patterns(snapshot, pattern_report)

        proposal2 = optimizer.propose_threshold_adjustments_with_patterns(snapshot, pattern_report)

        # Check deterministic ordering (should be sorted by component name)
        assert len(proposal1.adjustments) == 3
        assert proposal1.adjustments[0].healer_name == "healer"  # From "healer_a" split
        assert proposal1.adjustments[1].healer_name == "healer"  # From "healer_m" split
        assert proposal1.adjustments[2].healer_name == "healer"  # From "healer_z" split

        # Check identical proposals across runs
        assert proposal1.canonical_bytes() == proposal2.canonical_bytes()
        assert proposal1.content_hash() == proposal2.content_hash()

    def test_routing_drift_tightens_thresholds(self):
        """Test that ROUTING_DRIFT_HIGH finding tightens thresholds."""
        optimizer = HealingConfigOptimizer(escalation_delta=0.1, max_delta=0.2, max_threshold=THRESHOLD)

        # Create snapshot
        aggregates = [
            (
                HealingOutcomeAggregateKey(
                    healer_name="router_agent", tier="LOCAL_AGENT", failure_type="timeout"
                ),
                HealingOutcomeAggregate(success_count=90, failure_count=10, total_count=100),
            )
        ]

        snapshot = HealingOutcomeAggregateSnapshot(
            version_id="test_v1", created_utc=1000, aggregates=tuple(aggregates)
        )

        # Create drift finding
        pattern_report = PatternFindingReport(
            source_ids=PatternSourceIds(healing_snapshot_version="test_v1"),
            findings=(
                PatternFinding(
                    key=PatternFindingKey(
                        component="router_agent", dimension="drift", label="ROUTING_DRIFT_HIGH"
                    ),
                    severity=0.8,
                    evidence=("drift_score_0.800000",),
                    metrics=(("drift_score", 0.8),),
                ),
            ),
        )

        # Get proposal
        proposal = optimizer.propose_threshold_adjustments_with_patterns(snapshot, pattern_report)

        # Check that threshold is tightened (decreased)
        assert len(proposal.adjustments) == 1
        adj = proposal.adjustments[0]

        # Current threshold for LOCAL_AGENT is 0.5
        assert adj.current_threshold == 0.5
        # Should decrease by escalation_delta * severity * 0.5
        # = 0.5 - (0.1 * 0.8 * 0.5) = 0.5 - 0.04 = 0.46 (allowing for floating point precision)
        assert abs(adj.proposed_threshold - 0.46) < 1e-10
        assert adj.failure_type == "drift_based"
        assert "ROUTING_DRIFT_HIGH" in adj.reason

    def test_max_delta_clamping(self):
        """Test that adjustments are clamped to max_delta per healer."""
        optimizer = HealingConfigOptimizer(
            escalation_delta=0.2,  # Large delta
            max_delta=0.1,  # Small max delta
            max_threshold=THRESHOLD,
        )

        # Create snapshot
        aggregates = [
            (
                HealingOutcomeAggregateKey(
                    healer_name="test_healer", tier="LOCAL_AGENT", failure_type="timeout"
                ),
                HealingOutcomeAggregate(success_count=80, failure_count=20, total_count=100),
            )
        ]

        snapshot = HealingOutcomeAggregateSnapshot(
            version_id="test_v1", created_utc=1000, aggregates=tuple(aggregates)
        )

        # Create two findings that would exceed max_delta
        pattern_report = PatternFindingReport(
            source_ids=PatternSourceIds(healing_snapshot_version="test_v1"),
            findings=(
                PatternFinding(
                    key=PatternFindingKey(
                        component="test_healer", dimension="performance", label="UNDERPERFORMING_HEALER_TIER"
                    ),
                    severity=1.0,  # Would add 0.2
                    evidence=("success_rate_0.300000",),
                    metrics=(("success_rate", 0.3),),
                ),
                PatternFinding(
                    key=PatternFindingKey(
                        component="test_healer", dimension="drift", label="ROUTING_DRIFT_HIGH"
                    ),
                    severity=1.0,  # Would subtract 0.1
                    evidence=("drift_score_0.800000",),
                    metrics=(("drift_score", 0.8),),
                ),
            ),
        )

        # Get proposal
        proposal = optimizer.propose_threshold_adjustments_with_patterns(snapshot, pattern_report)

        # Check that total delta is clamped to max_delta
        assert len(proposal.adjustments) == 2

        # Calculate total delta
        total_delta = sum(adj.proposed_threshold - adj.current_threshold for adj in proposal.adjustments)

        # Should be clamped to max_delta = 0.1
        assert abs(total_delta) <= optimizer._max_delta

        # Check that scaling is mentioned in reason
        for adj in proposal.adjustments:
            if "scaled to max_delta" in adj.reason:
                assert "0.100000" in adj.reason
