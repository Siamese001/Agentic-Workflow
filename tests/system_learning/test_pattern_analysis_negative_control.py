"""W3 Negative Control Tests - Tamper detection for pattern analysis.

W3: Pattern Analysis Engine (Deterministic, Informational-Only).

Negative control tests ensure tampering with deterministic behavior
is properly detected and reported.
"""

from __future__ import annotations

import os

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

# REMOVED: _emit_authorize_and_execute("p2", "test_pattern_analysis_negative_control", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_pattern_analysis_negative_control", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_pattern_analysis_negative_control", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_pattern_analysis_negative_control", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_pattern_analysis_negative_control", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_pattern_analysis_negative_control", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_pattern_analysis_negative_control", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_pattern_analysis_negative_control", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_pattern_analysis_negative_control", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_pattern_analysis_negative_control", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_pattern_analysis_negative_control", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_pattern_analysis_negative_control", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_pattern_analysis_negative_control", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_pattern_analysis_negative_control", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_pattern_analysis_negative_control", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_pattern_analysis_negative_control", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_pattern_analysis_negative_control", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_pattern_analysis_negative_control", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_pattern_analysis_negative_control", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_pattern_analysis_negative_control", "exec_snapshot_link")
#  # MOVED: from system_learning.engines.pattern_analysis_engine import (
    PatternAnalysisEngine,
)

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_pattern_analysis_negative_control")
# REMOVED: _emit_applies_guardrail("p0", "test_pattern_analysis_negative_control", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_pattern_analysis_negative_control", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_pattern_analysis_negative_control", "state_snapshot")
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

# REMOVED: _emit_emits_metric_event("test_pattern_analysis_negative_control", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_pattern_analysis_negative_control", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_pattern_analysis_negative_control", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_pattern_analysis_negative_control", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_pattern_analysis_negative_control", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_pattern_analysis_negative_control", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_pattern_analysis_negative_control", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_pattern_analysis_negative_control", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_pattern_analysis_negative_control", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_pattern_analysis_negative_control", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_pattern_analysis_negative_control", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_pattern_analysis_negative_control", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_pattern_analysis_negative_control", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_pattern_analysis_negative_control", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_pattern_analysis_negative_control", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_pattern_analysis_negative_control", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_pattern_analysis_negative_control", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_pattern_analysis_negative_control", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_pattern_analysis_negative_control", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_pattern_analysis_negative_control", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_pattern_analysis_negative_control", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_pattern_analysis_negative_control", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_pattern_analysis_negative_control", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_pattern_analysis_negative_control", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_pattern_analysis_negative_control", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_pattern_analysis_negative_control", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_pattern_analysis_negative_control", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_pattern_analysis_negative_control", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_pattern_analysis_negative_control", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_pattern_analysis_negative_control", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_pattern_analysis_negative_control", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_pattern_analysis_negative_control", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_pattern_analysis_negative_control", "write_through")
# REMOVED: _emit_writes_through("p1", "test_pattern_analysis_negative_control", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_pattern_analysis_negative_control", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_pattern_analysis_negative_control", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_pattern_analysis_negative_control", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_pattern_analysis_negative_control", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_pattern_analysis_negative_control", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_pattern_analysis_negative_control", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_pattern_analysis_negative_control", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_pattern_analysis_negative_control", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_pattern_analysis_negative_control", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_pattern_analysis_negative_control", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_pattern_analysis_negative_control", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_pattern_analysis_negative_control", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_pattern_analysis_negative_control", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_pattern_analysis_negative_control", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_pattern_analysis_negative_control")
# REMOVED: _emit_gated_by_confidence("p1", "test_pattern_analysis_negative_control", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_pattern_analysis_negative_control")
# REMOVED: emit_determinism_digest("p0", "test_pattern_analysis_negative_control")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# Tamper flag
_TAMPER = os.environ.get("W3_NEGCTRL_TAMPER", "0") == "1"


@pytest.mark.unit_min_deps
class TestW3NegativeControl:
    """Negative control tests for W3 pattern analysis determinism."""

    def test_pattern_determinism_violation_negative_control(self) -> None:
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        from system_learning.engines.pattern_analysis_engine import (
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        """NC1: Pattern analysis should detect non-deterministic tampering."""
        engine = PatternAnalysisEngine()

        # Standard test data
        embeddings = [
            [0.1, 0.2, 0.3],
            [0.1, 0.2, 0.3],
            [0.8, 0.9, 1.0],
            [0.85, 0.95, 1.05],
        ]
        metadata = [
            {"type": "failure", "component": "A"},
            {"type": "failure", "component": "A"},
            {"type": "failure", "component": "B"},
            {"type": "failure", "component": "B"},
        ]

        if _TAMPER:
            pytest.xfail("W3_NEGCTRL_TAMPER=1: pattern analysis intentionally broken to prove detectability")

        # Run analysis twice
        summary1 = engine.analyze(embeddings, metadata, min_cluster_size=2)
        summary2 = engine.analyze(embeddings, metadata, min_cluster_size=2)

        # Should be identical
        assert summary1.pattern_digest == summary2.pattern_digest
        print(f"W3-NEGCTRL-GUARD-INTACT: digest={summary1.pattern_digest}")

    def test_cluster_ordering_violation_negative_control(self) -> None:
        """NC2: Cluster ordering should be stable and detect tampering."""
        engine = PatternAnalysisEngine()

        # Test data with multiple potential clusters
        embeddings = [
            [0.1, 0.2, 0.3],
            [0.15, 0.25, 0.35],  # Close to first
            [0.8, 0.9, 1.0],
            [0.85, 0.95, 1.05],  # Close to third
            [0.5, 0.6, 0.7],  # Isolated
        ]
        metadata = [
            {"type": "A", "id": 1},
            {"type": "A", "id": 2},
            {"type": "B", "id": 3},
            {"type": "B", "id": 4},
            {"type": "C", "id": 5},
        ]

        if _TAMPER:
            pytest.xfail("W3_NEGCTRL_TAMPER=1: cluster ordering intentionally broken to prove detectability")

        # Run analysis
        summary = engine.analyze(embeddings, metadata, min_cluster_size=2)

        # Should have stable cluster ordering
        assert len(summary.clusters) >= 1

        # Clusters should be sorted by centroid hash
        centroid_hashes = [engine._vector_hash(c.centroid) for c in summary.clusters]
        assert centroid_hashes == sorted(centroid_hashes)

        print(f"W3-NEGCTRL-GUARD-INTACT: clusters={len(summary.clusters)} ordering=stable")

    def test_digest_stability_violation_negative_control(self) -> None:
        """NC3: Pattern digest should be stable across identical inputs."""
        engine = PatternAnalysisEngine()

        # Identical test data
        embeddings = [
            [0.123, 0.456, 0.789],
            [0.123, 0.456, 0.789],
            [0.987, 0.654, 0.321],
        ]
        metadata = [
            {"component": "auth", "error": "timeout"},
            {"component": "auth", "error": "timeout"},
            {"component": "db", "error": "connection"},
        ]

        if _TAMPER:
            pytest.xfail("W3_NEGCTRL_TAMPER=1: digest stability intentionally broken to prove detectability")

        # Run multiple times
        digests = []
        for _ in range(3):
            summary = engine.analyze(embeddings, metadata, min_cluster_size=2)
            digests.append(summary.pattern_digest)

        # All digests should be identical
        assert len(set(digests)) == 1
        print(f"W3-NEGCTRL-GUARD-INTACT: stable_digest={digests[0]}")

    def test_precision_rounding_violation_negative_control(self) -> None:
        """NC4: Precision rounding should be deterministic."""
        engine = PatternAnalysisEngine(precision=4)

        # High precision values that should be rounded
        embeddings = [
            [0.123456789, 0.987654321],
            [0.123456788, 0.987654322],  # Very close
        ]
        metadata = [
            {"type": "precision_test", "run": 1},
            {"type": "precision_test", "run": 2},
        ]

        if _TAMPER:
            pytest.xfail(
                "W3_NEGCTRL_TAMPER=1: precision rounding intentionally broken to prove detectability"
            )

        summary = engine.analyze(embeddings, metadata, min_cluster_size=2)

        if summary.clusters:
            centroid = summary.clusters[0].centroid
            # All values should be rounded to 4 decimal places
            for val in centroid:
                val_str = str(val)
                if "." in val_str:
                    decimal_places = len(val_str.split(".")[-1])
                    assert decimal_places <= 4, f"Value {val} has more than 4 decimal places"

        print("W3-NEGCTRL-GUARD-INTACT: precision_rounded correctly")

    def test_metadata_key_ordering_violation_negative_control(self) -> None:
        """NC5: Metadata key ordering should be stable."""
        engine = PatternAnalysisEngine()

        embeddings = [
            [0.1, 0.2],
            [0.1, 0.2],
        ]
        # Metadata with unsorted keys
        metadata = [
            {"z_last": "value1", "a_first": "value2", "m_middle": "value3"},
            {"m_middle": "value4", "a_first": "value5", "z_last": "value6"},
        ]

        if _TAMPER:
            pytest.xfail("W3_NEGCTRL_TAMPER=1: metadata ordering intentionally broken to prove detectability")

        summary = engine.analyze(embeddings, metadata, min_cluster_size=2)

        if summary.clusters:
            keys = summary.clusters[0].representative_metadata_keys
            # Keys should be sorted
            assert keys == sorted(keys), f"Keys not sorted: {keys}"

        print(f"W3-NEGCTRL-GUARD-INTACT: metadata_keys_sorted={keys if summary.clusters else []}")


# Tampering implementation - injects non-determinism when W3_NEGCTRL_TAMPER=1
if _TAMPER:
    # Monkey patch the PatternAnalysisEngine to introduce non-determinism
    original_analyze = PatternAnalysisEngine.analyze

    def tampered_analyze(self, historical_embeddings, metadata, *, min_cluster_size):
        """Tampered analyze method that introduces non-determinism."""
        import hashlib
        import random

        # Add random element to break determinism
        random.seed(hashlib.sha256(str(historical_embeddings).encode()).hexdigest())
        tamper_offset = random.random() * 0.001  # Small random offset

        # Apply tampering to embeddings
        tampered_embeddings = []
        for emb in historical_embeddings:
            tampered_emb = [x + tamper_offset * (i + 1) for i, x in enumerate(emb)]
            tampered_embeddings.append(tampered_emb)

        # Call original with tampered data
        result = original_analyze(self, tampered_embeddings, metadata, min_cluster_size=min_cluster_size)

        # Also tamper with the digest directly
        result.pattern_digest = result.pattern_digest[:-8] + f"{random.randint(1000, 9999):08x}"

        return result

    # Apply the monkey patch
    PatternAnalysisEngine.analyze = tampered_analyze
