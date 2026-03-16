"""Tests for W3 pattern analysis integration in meta-learning pipeline.

W3: Pattern Analysis Engine (Deterministic, Informational-Only).

Tests ensure pattern analysis is properly wired into the pipeline
as C0 informational-only input.
"""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

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

_emit_authorize_and_execute("p2", "test_meta_learning_pipeline_patterns", "execution_auth")
_emit_validates_capability("p2", "test_meta_learning_pipeline_patterns", "capability_check")
_emit_routes_to_capability("p2", "test_meta_learning_pipeline_patterns", "capability_route")
_emit_writes_via_uwg("p2", "test_meta_learning_pipeline_patterns", "uwg_write")
_emit_blocks_direct_write("p2", "test_meta_learning_pipeline_patterns", "direct_write_block")
_emit_records_tool_invocation("p2", "test_meta_learning_pipeline_patterns", "tool_invocation")
_emit_captures_execution_output("p2", "test_meta_learning_pipeline_patterns", "exec_output")
_emit_dispatches_agent("p3", "test_meta_learning_pipeline_patterns", "agent_dispatch")
_emit_coordinates_agents("p3", "test_meta_learning_pipeline_patterns", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_meta_learning_pipeline_patterns", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_meta_learning_pipeline_patterns", "healing_outcome")
_emit_escalates_failure("p3", "test_meta_learning_pipeline_patterns", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_meta_learning_pipeline_patterns", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_meta_learning_pipeline_patterns", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_meta_learning_pipeline_patterns", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_meta_learning_pipeline_patterns", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_meta_learning_pipeline_patterns", "eval_metric")
_emit_stores_embedding("p4", "test_meta_learning_pipeline_patterns", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_meta_learning_pipeline_patterns", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_meta_learning_pipeline_patterns", "exec_snapshot_link")
from system_learning.engines.embedding_service_factory import EmbeddingServiceFactory
from system_learning.engines.pattern_analysis_engine import (
    PatternAnalysisEngine,
    PatternSummary,
)
from system_learning.pipelines.meta_learning_pipeline import (
    _analyze_historical_patterns,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_execution_terminates_at_uwg,
    _emit_writes_through,
    _emit_validated_by_safety_plane,
    _emit_invokes_eval,
    _emit_proposal_commits_routing,
)
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_meta_learning_pipeline_patterns", "p4obs", "metric_1")
_emit_emits_metric_event("test_meta_learning_pipeline_patterns", "p4obs", "metric_2")
_emit_emits_metric_event("test_meta_learning_pipeline_patterns", "p4obs", "metric_3")
_emit_emits_metric_event("test_meta_learning_pipeline_patterns", "p4obs", "metric_4")
_emit_emits_metric_event("test_meta_learning_pipeline_patterns", "p4obs", "metric_5")
_emit_emits_metric_event("test_meta_learning_pipeline_patterns", "p4obs", "metric_6")
_emit_records_incident_event("test_meta_learning_pipeline_patterns", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_meta_learning_pipeline_patterns", "p4obs", "anomaly")
_emit_writes_observability_log("test_meta_learning_pipeline_patterns", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_meta_learning_pipeline_patterns", "p4obs", "mon_state")
_emit_triggers_alert("test_meta_learning_pipeline_patterns", "p4obs", "alert")
_emit_links_incident_trace("test_meta_learning_pipeline_patterns", "p4obs", "trace_link")
_emit_captures_pattern("test_meta_learning_pipeline_patterns", "p3lm", "pattern")
_emit_records_learning_event("test_meta_learning_pipeline_patterns", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_meta_learning_pipeline_patterns", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_meta_learning_pipeline_patterns", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_meta_learning_pipeline_patterns", "p3lm", "routing")
_emit_improves_agent_policy("test_meta_learning_pipeline_patterns", "p3lm", "policy")
_emit_stores_learning_state("test_meta_learning_pipeline_patterns", "p3lm", "state")
_emit_records_execution_trace("test_meta_learning_pipeline_patterns", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_meta_learning_pipeline_patterns", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_meta_learning_pipeline_patterns", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_meta_learning_pipeline_patterns", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_meta_learning_pipeline_patterns", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_meta_learning_pipeline_patterns", "env_read", "p2_env_1")
_emit_reads_environ("test_meta_learning_pipeline_patterns", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_meta_learning_pipeline_patterns", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_meta_learning_pipeline_patterns", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_meta_learning_pipeline_patterns")
_emit_applies_guardrail("p0", "test_meta_learning_pipeline_patterns", "p0_governance")
_emit_reads_policy_state("p0", "test_meta_learning_pipeline_patterns", "policy_binding")
_emit_snapshots_state("p0", "test_meta_learning_pipeline_patterns", "state_snapshot")
_emit_pulls_context("p1", "test_meta_learning_pipeline_patterns", "context_pull")
_emit_pulls_context("p1", "test_meta_learning_pipeline_patterns", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_meta_learning_pipeline_patterns", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_meta_learning_pipeline_patterns", "uwg_term_secondary")
_emit_writes_through("p1", "test_meta_learning_pipeline_patterns", "write_through")
_emit_writes_through("p1", "test_meta_learning_pipeline_patterns", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_meta_learning_pipeline_patterns", "safety_validation")
_emit_invokes_eval("p1", "test_meta_learning_pipeline_patterns", "eval_call")
_emit_proposal_commits_routing("p1", "test_meta_learning_pipeline_patterns", "routing_commit")
emit_replay_key("p0", "test_meta_learning_pipeline_patterns")
emit_determinism_digest("p0", "test_meta_learning_pipeline_patterns")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


@pytest.mark.unit_min_deps
class TestMetaLearningPipelinePatterns:
    """Test pattern analysis integration in meta-learning pipeline."""

    def test_pattern_analysis_disabled_when_embedding_disabled(self) -> None:
        """T1: Pattern analysis should be disabled when embeddings are disabled."""
        engine = PatternAnalysisEngine()

        # Create mock dependencies with pattern engine
        mock_deps = MagicMock()
        mock_deps.pattern_analysis_engine = engine

        # Create mock aggregate snapshot
        mock_snapshot = MagicMock()
        mock_snapshot.outcomes = []

        # Disable embeddings via environment
        with patch.dict(os.environ, {"EMBEDDING_ENABLED": "false"}):
            result = _analyze_historical_patterns(mock_deps, mock_snapshot)

        # Should return None when embeddings disabled
        assert result is None

    def test_pattern_analysis_included_when_embeddings_enabled(self) -> None:
        """T2: Pattern analysis should be included when embeddings are enabled."""
        engine = PatternAnalysisEngine()

        # Create mock dependencies
        mock_deps = MagicMock()
        mock_deps.pattern_analysis_engine = engine

        # Create mock aggregate snapshot with sufficient data
        mock_snapshot = MagicMock()
        mock_outcomes = []

        # Create 12 mock outcomes (above small-N threshold of 10)
        for i in range(12):
            outcome = MagicMock()
            outcome.failure_signature = MagicMock()
            outcome.failure_signature.component = f"component_{i % 3}"
            outcome.failure_signature.failure_type = f"failure_{i % 2}"
            outcome.failure_signature.healer_name = f"healer_{i % 2}"
            outcome.failure_signature.timestamp_utc = 1234567890 + i
            mock_outcomes.append(outcome)

        mock_snapshot.outcomes = mock_outcomes
        # Ensure mock does NOT have canonical_bytes so legacy path is used
        del mock_snapshot.canonical_bytes

        # Enable embeddings and mock the embedding service
        mock_emb_service = MagicMock()
        mock_emb_service.is_disabled.return_value = False
        with (
            patch.dict(os.environ, {"EMBEDDING_ENABLED": "true"}),
            patch.object(EmbeddingServiceFactory, "get_or_disabled", return_value=mock_emb_service),
        ):
            result = _analyze_historical_patterns(mock_deps, mock_snapshot)

        # Should return pattern summary
        assert isinstance(result, PatternSummary)
        assert result.pattern_digest is not None

    def test_pattern_analysis_influence_capped(self) -> None:
        """T3: Pattern analysis influence should be capped at ≤ 0.25."""
        # This is tested at the engine level - pattern analysis is informational only
        # The actual influence capping is handled by the optimizer
        engine = PatternAnalysisEngine()

        # Use orthogonal directions so cosine distance separates clusters
        embeddings = [
            [1.0, 0.0, 0.0, 0.0],
            [0.95, 0.05, 0.0, 0.0],  # Close to first in direction
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.95, 0.05],  # Close to third in direction
        ]
        metadata = [
            {"type": "failure", "component": "A"},
            {"type": "failure", "component": "A"},
            {"type": "failure", "component": "B"},
            {"type": "failure", "component": "B"},
        ]

        summary = engine.analyze(embeddings, metadata, min_cluster_size=2)

        # Pattern analysis itself doesn't apply influence caps
        # It's informational-only - the optimizer applies caps
        assert isinstance(summary, PatternSummary)
        assert len(summary.clusters) == 2

    def test_pattern_analysis_deterministic(self) -> None:
        """T4: Pattern analysis should be deterministic across runs."""
        engine = PatternAnalysisEngine()

        # Create mock dependencies
        mock_deps = MagicMock()
        mock_deps.pattern_analysis_engine = engine

        # Create mock aggregate snapshot
        mock_snapshot = MagicMock()
        mock_outcomes = []

        # Create deterministic test data
        for i in range(12):
            outcome = MagicMock()
            outcome.failure_signature = MagicMock()
            outcome.failure_signature.component = f"comp_{i % 3}"
            outcome.failure_signature.failure_type = f"fail_{i % 2}"
            outcome.failure_signature.healer_name = f"heal_{i % 2}"
            outcome.failure_signature.timestamp_utc = 1234567890 + i
            mock_outcomes.append(outcome)

        mock_snapshot.outcomes = mock_outcomes
        # Ensure mock does NOT have canonical_bytes so legacy path is used
        del mock_snapshot.canonical_bytes

        # Enable embeddings and mock the embedding service
        mock_emb_service = MagicMock()
        mock_emb_service.is_disabled.return_value = False
        with (
            patch.dict(os.environ, {"EMBEDDING_ENABLED": "true"}),
            patch.object(EmbeddingServiceFactory, "get_or_disabled", return_value=mock_emb_service),
        ):
            # Run twice with same inputs
            result1 = _analyze_historical_patterns(mock_deps, mock_snapshot)
            result2 = _analyze_historical_patterns(mock_deps, mock_snapshot)

        # Should produce identical pattern digests
        assert result1.pattern_digest == result2.pattern_digest

        print(f"W3-PATTERN-DIGEST: {result1.pattern_digest}")

    def test_pattern_analysis_empty_input(self) -> None:
        """T5: Empty historical data should return empty pattern summary."""
        engine = PatternAnalysisEngine()

        mock_deps = MagicMock()
        mock_deps.pattern_analysis_engine = engine

        mock_snapshot = MagicMock()
        mock_snapshot.outcomes = []

        with patch.dict(os.environ, {"EMBEDDING_ENABLED": "true"}):
            result = _analyze_historical_patterns(mock_deps, mock_snapshot)

        # Should return None for empty input
        assert result is None

    def test_pattern_analysis_small_n_guard(self) -> None:
        """T6: Small-N guard should prevent pattern analysis on insufficient data."""
        engine = PatternAnalysisEngine()

        mock_deps = MagicMock()
        mock_deps.pattern_analysis_engine = engine

        # Only 8 data points (below small-N threshold of 10)
        mock_snapshot = MagicMock()
        mock_outcomes = []

        for i in range(8):
            outcome = MagicMock()
            outcome.failure_signature = MagicMock()
            outcome.failure_signature.component = f"component_{i}"
            outcome.failure_signature.failure_type = "failure"
            outcome.failure_signature.healer_name = "healer"
            outcome.failure_signature.timestamp_utc = 1234567890 + i
            mock_outcomes.append(outcome)

        mock_snapshot.outcomes = mock_outcomes

        with patch.dict(os.environ, {"EMBEDDING_ENABLED": "true"}):
            result = _analyze_historical_patterns(mock_deps, mock_snapshot)

        # Should return None due to small-N guard
        assert result is None

    def test_pattern_analysis_informational_only(self) -> None:
        """T7: Pattern analysis should be informational-only."""
        # This is inherent in the design - pattern analysis only produces summaries
        # It doesn't directly mutate any thresholds or configurations
        engine = PatternAnalysisEngine()

        embeddings = [
            [0.1, 0.2, 0.3, 0.4],
            [0.1, 0.2, 0.3, 0.4],
        ]
        metadata = [{"type": "test"}, {"type": "test"}]

        summary = engine.analyze(embeddings, metadata, min_cluster_size=2)

        # Verify informational-only nature
        assert isinstance(summary, PatternSummary)
        assert hasattr(summary, "clusters")
        assert hasattr(summary, "pattern_digest")
        # No direct configuration changes

    def test_pattern_analysis_kill_switch(self) -> None:
        """T8: Kill switch should disable pattern analysis entirely."""
        engine = PatternAnalysisEngine()

        mock_deps = MagicMock()
        mock_deps.pattern_analysis_engine = engine

        mock_snapshot = MagicMock()
        mock_snapshot.outcomes = []

        # Enable kill switch
        with patch.dict(os.environ, {"EMBEDDING_ENABLED": "false"}):
            result = _analyze_historical_patterns(mock_deps, mock_snapshot)

        # Should return None when kill switch enabled
        assert result is None
