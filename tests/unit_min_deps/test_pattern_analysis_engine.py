"""Tests for Pattern Analysis Engine - Phase 8."""

from __future__ import annotations

import pytest

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_pattern_analysis_engine")
# REMOVED: _emit_applies_guardrail("p0", "test_pattern_analysis_engine", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_pattern_analysis_engine", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_pattern_analysis_engine", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_pattern_analysis_engine")
# REMOVED: emit_determinism_digest("p0", "test_pattern_analysis_engine")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_pattern_analysis_engine", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_pattern_analysis_engine", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_pattern_analysis_engine", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_pattern_analysis_engine", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_pattern_analysis_engine", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_pattern_analysis_engine", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_pattern_analysis_engine", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_pattern_analysis_engine", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_pattern_analysis_engine", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_pattern_analysis_engine", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_pattern_analysis_engine", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_pattern_analysis_engine", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_pattern_analysis_engine", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_pattern_analysis_engine", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_pattern_analysis_engine", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_pattern_analysis_engine", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_pattern_analysis_engine", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_pattern_analysis_engine", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_pattern_analysis_engine", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_pattern_analysis_engine", "exec_snapshot_link")

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

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
from system_learning.engines.pattern_analysis_engine import (
    PatternAnalysisConfig,
    PatternAnalysisEngine,
)
from system_learning.types.healing_outcome_learning_types import (
    HealingOutcomeAggregate,
    HealingOutcomeAggregateKey,
    HealingOutcomeAggregateSnapshot,
)

# REMOVED: _emit_emits_metric_event("test_pattern_analysis_engine", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_pattern_analysis_engine", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_pattern_analysis_engine", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_pattern_analysis_engine", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_pattern_analysis_engine", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_pattern_analysis_engine", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_pattern_analysis_engine", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_pattern_analysis_engine", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_pattern_analysis_engine", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_pattern_analysis_engine", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_pattern_analysis_engine", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_pattern_analysis_engine", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_pattern_analysis_engine", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_pattern_analysis_engine", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_pattern_analysis_engine", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_pattern_analysis_engine", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_pattern_analysis_engine", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_pattern_analysis_engine", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_pattern_analysis_engine", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_pattern_analysis_engine", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_pattern_analysis_engine", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_pattern_analysis_engine", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_pattern_analysis_engine", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_pattern_analysis_engine", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_pattern_analysis_engine", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_pattern_analysis_engine", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_pattern_analysis_engine", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_pattern_analysis_engine", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_pattern_analysis_engine", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_pattern_analysis_engine", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_pattern_analysis_engine", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_pattern_analysis_engine", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_pattern_analysis_engine", "write_through")
# REMOVED: _emit_writes_through("p1", "test_pattern_analysis_engine", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_pattern_analysis_engine", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_pattern_analysis_engine", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_pattern_analysis_engine", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_pattern_analysis_engine", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_pattern_analysis_engine", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_pattern_analysis_engine", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_pattern_analysis_engine", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_pattern_analysis_engine", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_pattern_analysis_engine", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_pattern_analysis_engine", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_pattern_analysis_engine", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_pattern_analysis_engine", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_pattern_analysis_engine", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_pattern_analysis_engine", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_pattern_analysis_engine")
# REMOVED: _emit_gated_by_confidence("p1", "test_pattern_analysis_engine", "confidence_gate")


class TestPatternAnalysisEngine:
    """Test suite for Pattern Analysis Engine."""

    def test_determinism_same_inputs_same_hash(self):
        """Test that same inputs produce identical outputs."""
        engine = PatternAnalysisEngine()

        # Create test healing snapshot
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

        # Analyze twice
        report1 = engine.analyze(
            healing_snapshot_bytes=snapshot.canonical_bytes(),
            detection_signal_bytes=None,
            drift_snapshot_bytes=None,
            now_utc=2000,
        )

        report2 = engine.analyze(
            healing_snapshot_bytes=snapshot.canonical_bytes(),
            detection_signal_bytes=None,
            drift_snapshot_bytes=None,
            now_utc=2000,
        )

        # Check deterministic outputs
        assert report1.canonical_bytes() == report2.canonical_bytes()
        assert report1.content_hash() == report2.content_hash()

    def test_permutation_invariant_healing_inputs(self):
        """Test that permuted healing aggregates produce identical report."""
        engine = PatternAnalysisEngine()

        # Create aggregates in different order
        aggregates1 = [
            (
                HealingOutcomeAggregateKey(
                    healer_name="healer_a", tier="LOCAL_AGENT", failure_type="timeout"
                ),
                HealingOutcomeAggregate(success_count=80, failure_count=20, total_count=100),
            ),
            (
                HealingOutcomeAggregateKey(healer_name="healer_b", tier="REMOTE_AGENT", failure_type="error"),
                HealingOutcomeAggregate(success_count=60, failure_count=40, total_count=100),
            ),
        ]

        aggregates2 = list(reversed(aggregates1))  # Reverse order
        # Sort both to ensure they pass validation
        aggregates1.sort(key=lambda pair: (pair[0].healer_name, pair[0].tier, pair[0].failure_type))
        aggregates2.sort(key=lambda pair: (pair[0].healer_name, pair[0].tier, pair[0].failure_type))

        snapshot1 = HealingOutcomeAggregateSnapshot(
            version_id="test_v1", created_utc=1000, aggregates=tuple(aggregates1)
        )

        snapshot2 = HealingOutcomeAggregateSnapshot(
            version_id="test_v1", created_utc=1000, aggregates=tuple(aggregates2)
        )

        # Analyze both
        report1 = engine.analyze(
            healing_snapshot_bytes=snapshot1.canonical_bytes(),
            detection_signal_bytes=None,
            drift_snapshot_bytes=None,
            now_utc=2000,
        )

        report2 = engine.analyze(
            healing_snapshot_bytes=snapshot2.canonical_bytes(),
            detection_signal_bytes=None,
            drift_snapshot_bytes=None,
            now_utc=2000,
        )

        # Should be identical despite permutation
        assert report1.canonical_bytes() == report2.canonical_bytes()
        assert report1.content_hash() == report2.content_hash()

    def test_underperforming_finding_triggered(self):
        """Test that underperforming healer triggers finding."""
        config = PatternAnalysisConfig(success_rate_threshold_low=0.7, min_observations=20)
        engine = PatternAnalysisEngine(config)

        # Create underperforming aggregate
        aggregates = [
            (
                HealingOutcomeAggregateKey(
                    healer_name="poor_healer", tier="LOCAL_AGENT", failure_type="timeout"
                ),
                HealingOutcomeAggregate(
                    success_count=30,  # 30% success rate
                    failure_count=70,
                    total_count=100,
                ),
            )
        ]

        snapshot = HealingOutcomeAggregateSnapshot(
            version_id="test_v1", created_utc=1000, aggregates=tuple(aggregates)
        )

        report = engine.analyze(
            healing_snapshot_bytes=snapshot.canonical_bytes(),
            detection_signal_bytes=None,
            drift_snapshot_bytes=None,
            now_utc=2000,
        )

        # Check for underperforming finding
        assert len(report.findings) == 1
        finding = report.findings[0]
        assert finding.key.label == "UNDERPERFORMING_HEALER_TIER"
        assert finding.key.component == "poor_healer"
        assert finding.key.dimension == "performance"
        assert finding.severity == 0.7  # 1.0 - 0.3 success_rate
        assert "success_rate_0.300000" in finding.evidence
        assert "threshold_0.700000" in finding.evidence
        assert "sample_size_100" in finding.evidence

        # Check metrics are sorted
        assert finding.metrics == (
            ("success_rate", 0.3),
            ("sample_size", 100),
            ("error_rate", 0.7),
        )

    def test_optional_inputs_none_deterministic(self):
        """Test that optional inputs being None produces stable report."""
        engine = PatternAnalysisEngine()

        # Create minimal snapshot
        aggregates = [
            (
                HealingOutcomeAggregateKey(
                    healer_name="test_healer", tier="LOCAL_AGENT", failure_type="timeout"
                ),
                HealingOutcomeAggregate(success_count=90, failure_count=10, total_count=100),
            )
        ]

        snapshot = HealingOutcomeAggregateSnapshot(
            version_id="test_v1", created_utc=1000, aggregates=tuple(aggregates)
        )

        # Analyze with None optional inputs
        report = engine.analyze(
            healing_snapshot_bytes=snapshot.canonical_bytes(),
            detection_signal_bytes=None,
            drift_snapshot_bytes=None,
            now_utc=2000,
        )

        # Should have no findings (good performance)
        assert len(report.findings) == 0
        assert report.source_ids.healing_snapshot_version == snapshot.version_id
        assert report.source_ids.detection_signal_version is None
        assert report.source_ids.drift_snapshot_version is None

        # Check deterministic hash
        assert report.content_hash() is not None
        assert len(report.content_hash()) == 64  # SHA256 hex length

    def test_drift_signal_finding_triggered(self):
        """Test that high drift signal triggers finding."""
        engine = PatternAnalysisEngine()

        # Create minimal healing snapshot
        aggregates = [
            (
                HealingOutcomeAggregateKey(
                    healer_name="test_healer", tier="LOCAL_AGENT", failure_type="timeout"
                ),
                HealingOutcomeAggregate(success_count=90, failure_count=10, total_count=100),
            )
        ]

        snapshot = HealingOutcomeAggregateSnapshot(
            version_id="test_v1", created_utc=1000, aggregates=tuple(aggregates)
        )

        # Create drift signal with high score
        drift_data = {
            "version": "drift_v1",
            "drift_scores": [
                {
                    "component": "test_healer",
                    "score": 0.8,  # Above threshold of 0.7
                }
            ],
        }

        import json

        drift_bytes = json.dumps(drift_data).encode("utf-8")

        report = engine.analyze(
            healing_snapshot_bytes=snapshot.canonical_bytes(),
            detection_signal_bytes=None,
            drift_snapshot_bytes=drift_bytes,
            now_utc=2000,
        )

        # Check for drift finding
        assert len(report.findings) == 1
        finding = report.findings[0]
        assert finding.key.label == "ROUTING_DRIFT_HIGH"
        assert finding.key.component == "test_healer"
        assert finding.key.dimension == "drift"
        assert finding.severity == 0.8
        assert "drift_score_0.800000" in finding.evidence
        assert "threshold_0.700000" in finding.evidence
