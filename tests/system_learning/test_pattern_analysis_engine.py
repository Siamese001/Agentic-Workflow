"""Tests for W3 Pattern Analysis Engine.

W3: Pattern Analysis Engine (Deterministic, Informational-Only).

Tests ensure deterministic clustering, stable digests, and proper
handling of edge cases.
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
#  # MOVED: from system_learning.engines.pattern_analysis_engine import (
    PatternAnalysisEngine,
    PatternSummary,
)

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_pattern_analysis_engine")
# REMOVED: _emit_applies_guardrail("p0", "test_pattern_analysis_engine", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_pattern_analysis_engine", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_pattern_analysis_engine", "state_snapshot")
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
# REMOVED: emit_replay_key("p0", "test_pattern_analysis_engine")
# REMOVED: emit_determinism_digest("p0", "test_pattern_analysis_engine")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


@pytest.mark.unit_min_deps
class TestPatternAnalysisEngine:
    """Test suite for PatternAnalysisEngine."""

    def test_empty_input_returns_empty_summary(self) -> None:
                from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
                from system_learning.engines.pattern_analysis_engine import (
                from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
                """T1: Empty input should return empty summary with deterministic digest."""
                engine = PatternAnalysisEngine()

        engine = PatternAnalysisEngine()

        summary = engine.analyze([], [], min_cluster_size=2)

        assert isinstance(summary, PatternSummary)
        assert summary.clusters == []
        assert (
            summary.pattern_digest == "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945"
        )  # SHA-256 of []

    def test_single_embedding_returns_empty(self) -> None:
        """T2: Single embedding should return empty clusters."""
        engine = PatternAnalysisEngine()

        embeddings = [[0.1, 0.2, 0.3]]
        metadata = [{"type": "test", "id": 1}]

        summary = engine.analyze(embeddings, metadata, min_cluster_size=2)

        assert summary.clusters == []
        assert summary.pattern_digest == "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945"

    def test_deterministic_clustering_identical_inputs(self) -> None:
        """T3: Identical inputs should produce identical clusters and digest."""
        engine = PatternAnalysisEngine()

        # Use orthogonal directions so cosine distance separates them
        embeddings = [
            [1.0, 0.0, 0.0],
            [0.95, 0.05, 0.0],  # Close to first in direction
            [0.0, 1.0, 0.0],
            [0.05, 0.95, 0.0],  # Close to third in direction
        ]
        metadata = [
            {"type": "A", "id": 1},
            {"type": "A", "id": 2},
            {"type": "B", "id": 3},
            {"type": "B", "id": 4},
        ]

        summary1 = engine.analyze(embeddings, metadata, min_cluster_size=2)
        summary2 = engine.analyze(embeddings, metadata, min_cluster_size=2)

        # Should produce identical results
        assert summary1.pattern_digest == summary2.pattern_digest
        assert len(summary1.clusters) == len(summary2.clusters)

        # Print digest for determinism proof
        print(f"W3-PATTERN-DIGEST: {summary1.pattern_digest}")

        # Verify cluster structure
        assert len(summary1.clusters) == 2  # Two clusters formed

        # Clusters should have size 2 each
        for cluster in summary1.clusters:
            assert cluster.cluster_size == 2
            assert len(cluster.centroid) == 3
            assert "type" in cluster.representative_metadata_keys
            assert "id" in cluster.representative_metadata_keys

    def test_deterministic_clustering_different_order(self) -> None:
        """T4: Input order should not affect output (deterministic sorting)."""
        engine = PatternAnalysisEngine()

        embeddings = [
            [0.0, 1.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.05, 0.95, 0.0],
            [0.95, 0.05, 0.0],
        ]
        metadata = [
            {"type": "B", "id": 3},
            {"type": "A", "id": 1},
            {"type": "B", "id": 4},
            {"type": "A", "id": 2},
        ]

        # Run with original order
        summary1 = engine.analyze(embeddings, metadata, min_cluster_size=2)

        # Run with shuffled order
        shuffled_embeddings = list(zip(embeddings, metadata))
        import random

        random.seed(42)  # Fixed seed for reproducible shuffle
        random.shuffle(shuffled_embeddings)
        embeddings_shuffled, metadata_shuffled = zip(*shuffled_embeddings)

        summary2 = engine.analyze(list(embeddings_shuffled), list(metadata_shuffled), min_cluster_size=2)

        # Should produce identical results despite input order
        assert summary1.pattern_digest == summary2.pattern_digest
        assert len(summary1.clusters) == len(summary2.clusters)

        print(f"W3-PATTERN-DIGEST: {summary1.pattern_digest}")

    def test_min_cluster_size_filter(self) -> None:
        """T5: Clusters smaller than min_cluster_size should be filtered out."""
        engine = PatternAnalysisEngine()

        # Use orthogonal directions: two vectors in x-direction, one in y-direction
        embeddings = [
            [1.0, 0.0, 0.0],
            [0.95, 0.05, 0.0],  # Close to first in direction
            [0.0, 1.0, 0.0],  # Orthogonal single point
        ]
        metadata = [
            {"type": "A", "id": 1},
            {"type": "A", "id": 2},
            {"type": "B", "id": 3},
        ]

        # With min_cluster_size=2, should keep the size-2 cluster
        summary = engine.analyze(embeddings, metadata, min_cluster_size=2)
        assert len(summary.clusters) == 1
        assert summary.clusters[0].cluster_size == 2

        # With min_cluster_size=3, should filter out all clusters
        summary = engine.analyze(embeddings, metadata, min_cluster_size=3)
        assert len(summary.clusters) == 0

    def test_precision_rounding(self) -> None:
        """T6: Float precision should be rounded for determinism."""
        engine = PatternAnalysisEngine(precision=3)

        embeddings = [
            [0.123456, 0.654321],
            [0.123457, 0.654322],  # Very close
        ]
        metadata = [{"type": "test", "id": i} for i in range(2)]

        summary = engine.analyze(embeddings, metadata, min_cluster_size=2)

        # Centroid should be rounded to 3 decimal places
        if summary.clusters:
            centroid = summary.clusters[0].centroid
            for val in centroid:
                # Check that value has at most 3 decimal places
                assert len(str(val).split(".")[-1]) <= 3

    def test_mismatched_lengths_raises_error(self) -> None:
        """T7: Mismatched embedding and metadata lengths should raise ValueError."""
        engine = PatternAnalysisEngine()

        embeddings = [[0.1, 0.2], [0.3, 0.4]]
        metadata = [{"type": "test"}]  # Only one metadata entry

        with pytest.raises(ValueError, match="Embeddings and metadata must have same length"):
            engine.analyze(embeddings, metadata, min_cluster_size=2)

    def test_high_dimensional_vectors(self) -> None:
        """T8: Should handle high-dimensional vectors correctly."""
        engine = PatternAnalysisEngine()

        # 100-dimensional vectors with orthogonal directions
        # Two near-identical vectors + one orthogonal
        v1 = [0.0] * 100
        v1[0] = 1.0  # Points along dim 0
        v2 = [0.0] * 100
        v2[0] = 0.95
        v2[1] = 0.05  # Near dim 0
        v3 = [0.0] * 100
        v3[50] = 1.0  # Points along dim 50 (orthogonal)
        embeddings = [v1, v2, v3]
        metadata = [{"type": "A", "id": i} for i in range(3)]

        summary = engine.analyze(embeddings, metadata, min_cluster_size=2)

        # Should find one cluster of size 2 (v1 and v2)
        assert len(summary.clusters) == 1
        assert summary.clusters[0].cluster_size == 2
        assert len(summary.clusters[0].centroid) == 100

    def test_cluster_metadata_keys_stable_ordering(self) -> None:
        """T9: Metadata keys should have stable ordering."""
        engine = PatternAnalysisEngine()

        embeddings = [
            [0.1, 0.2],
            [0.1, 0.2],
        ]
        metadata = [
            {"z_key": "last", "a_key": "first", "m_key": "middle"},
            {"m_key": "middle2", "a_key": "first2", "z_key": "last2"},
        ]

        summary = engine.analyze(embeddings, metadata, min_cluster_size=2)

        if summary.clusters:
            keys = summary.clusters[0].representative_metadata_keys
            # Keys should be sorted and deduplicated
            expected_keys = ["a_key", "m_key", "z_key"]
            assert keys == expected_keys
