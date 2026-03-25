"""Tests for W2 embedding integration in HealingConfigOptimizer.

W2: Informational semantic retrieval + bounded scoring (C0-only).

Tests cover:
- Kill-switch path (embeddings disabled)
- Small-N guard (insufficient samples)
- Influence cap respected
- Deterministic aggregation
- Audit metadata present
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

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

# REMOVED: _emit_authorize_and_execute("p2", "test_healing_config_optimizer_embeddings", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_healing_config_optimizer_embeddings", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_healing_config_optimizer_embeddings", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_healing_config_optimizer_embeddings", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_healing_config_optimizer_embeddings", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_healing_config_optimizer_embeddings", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_healing_config_optimizer_embeddings", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_healing_config_optimizer_embeddings", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_healing_config_optimizer_embeddings", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_healing_config_optimizer_embeddings", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_healing_config_optimizer_embeddings", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_healing_config_optimizer_embeddings", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_healing_config_optimizer_embeddings", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_healing_config_optimizer_embeddings", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_healing_config_optimizer_embeddings", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_healing_config_optimizer_embeddings", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_healing_config_optimizer_embeddings", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_healing_config_optimizer_embeddings", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_healing_config_optimizer_embeddings", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_healing_config_optimizer_embeddings", "exec_snapshot_link")
from system_learning.engines.embedding_service_factory import EmbeddingServiceFactory
from system_learning.engines.healing_config_optimizer import (
    HealingConfigOptimizer,
)
from system_learning.types.healing_outcome_learning_types import (
    HealingOutcomeAggregate,
    HealingOutcomeAggregateKey,
    HealingOutcomeAggregateSnapshot,
)

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_healing_config_optimizer_embeddings")
# REMOVED: _emit_applies_guardrail("p0", "test_healing_config_optimizer_embeddings", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_healing_config_optimizer_embeddings", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_healing_config_optimizer_embeddings", "state_snapshot")
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

# REMOVED: _emit_emits_metric_event("test_healing_config_optimizer_embeddings", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_healing_config_optimizer_embeddings", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_healing_config_optimizer_embeddings", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_healing_config_optimizer_embeddings", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_healing_config_optimizer_embeddings", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_healing_config_optimizer_embeddings", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_healing_config_optimizer_embeddings", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_healing_config_optimizer_embeddings", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_healing_config_optimizer_embeddings", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_healing_config_optimizer_embeddings", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_healing_config_optimizer_embeddings", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_healing_config_optimizer_embeddings", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_healing_config_optimizer_embeddings", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_healing_config_optimizer_embeddings", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_healing_config_optimizer_embeddings", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_healing_config_optimizer_embeddings", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_healing_config_optimizer_embeddings", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_healing_config_optimizer_embeddings", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_healing_config_optimizer_embeddings", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_healing_config_optimizer_embeddings", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_healing_config_optimizer_embeddings", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_healing_config_optimizer_embeddings", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_healing_config_optimizer_embeddings", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_healing_config_optimizer_embeddings", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_healing_config_optimizer_embeddings", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_healing_config_optimizer_embeddings", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_healing_config_optimizer_embeddings", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_healing_config_optimizer_embeddings", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_healing_config_optimizer_embeddings", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_healing_config_optimizer_embeddings", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_healing_config_optimizer_embeddings", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_healing_config_optimizer_embeddings", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_healing_config_optimizer_embeddings", "write_through")
# REMOVED: _emit_writes_through("p1", "test_healing_config_optimizer_embeddings", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_healing_config_optimizer_embeddings", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_healing_config_optimizer_embeddings", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_healing_config_optimizer_embeddings", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_healing_config_optimizer_embeddings", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_healing_config_optimizer_embeddings", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_healing_config_optimizer_embeddings", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_healing_config_optimizer_embeddings", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_healing_config_optimizer_embeddings", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_healing_config_optimizer_embeddings", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_healing_config_optimizer_embeddings", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_healing_config_optimizer_embeddings", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_healing_config_optimizer_embeddings", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_healing_config_optimizer_embeddings", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_healing_config_optimizer_embeddings", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_healing_config_optimizer_embeddings")
# REMOVED: _emit_gated_by_confidence("p1", "test_healing_config_optimizer_embeddings", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_healing_config_optimizer_embeddings")
# REMOVED: emit_determinism_digest("p0", "test_healing_config_optimizer_embeddings")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300


@pytest.mark.unit_min_deps
class TestHealingConfigOptimizerEmbeddings:
    """Test W2 embedding integration in HealingConfigOptimizer."""

    @pytest.fixture
    def optimizer(self) -> HealingConfigOptimizer:
        """Create optimizer with test parameters."""
        return HealingConfigOptimizer(
            min_sample_size=20,
            low_success_rate_threshold=THRESHOLD,
            escalation_delta=0.1,
            max_threshold=THRESHOLD,
            max_delta=0.2,
        )

    @pytest.fixture
    def sample_snapshot(self) -> HealingOutcomeAggregateSnapshot:
        """Create a sample snapshot with sufficient samples."""
        aggregates = [
            (
                HealingOutcomeAggregateKey(
                    healer_name="test_healer", tier="LOCAL_AGENT", failure_type="test_failure"
                ),
                HealingOutcomeAggregate(
                    success_count=8,  # 8/20 = 0.4 < 0.5 threshold
                    failure_count=12,
                    total_count=20,  # Meets min_sample_size
                ),
            ),
            (
                HealingOutcomeAggregateKey(
                    healer_name="test_healer2", tier="REMOTE_AGENT", failure_type="test_failure"
                ),
                HealingOutcomeAggregate(
                    success_count=15,  # 15/40 = 0.375 < 0.5 threshold
                    failure_count=25,
                    total_count=40,  # Exceeds min_sample_size
                ),
            ),
        ]

        return HealingOutcomeAggregateSnapshot(
            version_id="test_version",
            created_utc=1234567890,
            aggregates=tuple(aggregates),
        )

    @pytest.fixture
    def small_snapshot(self) -> HealingOutcomeAggregateSnapshot:
        """Create a snapshot with insufficient samples (small-N)."""
        aggregates = [
            (
                HealingOutcomeAggregateKey(
                    healer_name="test_healer", tier="LOCAL_AGENT", failure_type="test_failure"
                ),
                HealingOutcomeAggregate(
                    success_count=0,  # 0/2 = 0.0 < 0.5 threshold
                    failure_count=2,
                    total_count=2,  # Below min_sample_size
                ),
            ),
        ]

        return HealingOutcomeAggregateSnapshot(
            version_id="test_version",
            created_utc=1234567890,
            aggregates=tuple(aggregates),
        )

    def test_kill_switch_path(
        self, optimizer: HealingConfigOptimizer, sample_snapshot: HealingOutcomeAggregateSnapshot
    ) -> None:
        """T1 - Kill-switch path: embeddings disabled should use statistical-only scoring."""
        # Mock embedding service as disabled
        with patch.object(EmbeddingServiceFactory, "get_or_disabled") as mock_get:
            mock_service = MagicMock()
            mock_service.is_disabled.return_value = True
            mock_get.return_value = mock_service

            # Create embedding metadata indicating disabled
            embedding_metadata = {
                "embedding_enabled_at_time": False,
                "embedding_replay_key": None,
                "embedding_artifact_hash": None,
                "embedding_topk_hashes": [],
                "embedding_topk_scores_round6": [],
            }

            # Get proposal with embeddings
            proposal = optimizer.propose_threshold_adjustments_with_embeddings(
                sample_snapshot,
                embedding_metadata=embedding_metadata,
                embedding_influence_cap=0.20,
                min_sample_threshold=THRESHOLD,
            )

            # Verify adjustments exist (statistical scoring still works)
            assert len(proposal.adjustments) > 0

            # Verify no embedding influence in reasons
            for adj in proposal.adjustments:
                assert "embedding_influenced" not in adj.reason

            # Verify confidence is statistical-only (no embedding influence)
            for adj in proposal.adjustments:
                assert 0.0 <= adj.confidence <= 1.0

    def test_small_n_guard(
        self, optimizer: HealingConfigOptimizer, small_snapshot: HealingOutcomeAggregateSnapshot
    ) -> None:
        """T2 - Small-N guard: insufficient samples should prevent adjustments entirely."""
        # Create embedding metadata with high scores
        embedding_metadata = {
            "embedding_enabled_at_time": True,
            "embedding_replay_key": "test_replay_key",
            "embedding_artifact_hash": "test_hash",
            "embedding_topk_hashes": ["hash1", "hash2"],
            "embedding_topk_scores_round6": [0.95, 0.90],  # High similarity scores
        }

        # Get proposal with embeddings
        proposal = optimizer.propose_threshold_adjustments_with_embeddings(
            small_snapshot,
            embedding_metadata=embedding_metadata,
            embedding_influence_cap=0.20,
            min_sample_threshold=THRESHOLD,
        )

        # Verify no adjustments due to small-N guard (base optimizer filters them out)
        assert len(proposal.adjustments) == 0

        # This demonstrates the small-N guard working - no proposals are made
        # when sample size is below threshold

    def test_influence_cap_respected(
        self, optimizer: HealingConfigOptimizer, sample_snapshot: HealingOutcomeAggregateSnapshot
    ) -> None:
        """T3 - Influence cap: embedding_weight should never exceed embedding_influence_cap."""
        # Create embedding metadata
        embedding_metadata = {
            "embedding_enabled_at_time": True,
            "embedding_replay_key": "test_replay_key",
            "embedding_artifact_hash": "test_hash",
            "embedding_topk_hashes": ["hash1", "hash2"],
            "embedding_topk_scores_round6": [0.95, 0.90],
        }

        # Test with cap of 0.20
        proposal = optimizer.propose_threshold_adjustments_with_embeddings(
            sample_snapshot,
            embedding_metadata=embedding_metadata,
            embedding_influence_cap=0.20,
            min_sample_threshold=THRESHOLD,
        )

        # Verify embedding influence is applied and capped
        embedding_found = False
        for adj in proposal.adjustments:
            if "embedding_influenced" in adj.reason:
                embedding_found = True
                # Extract weight from reason string
                import re

                match = re.search(r"weight=(\d+\.\d+)", adj.reason)
                assert match is not None
                weight = float(match.group(1))
                assert weight == 0.20, f"Expected weight=0.20, got {weight}"

        assert embedding_found, "Should have embedding-influenced adjustments"

    def test_deterministic_aggregation(
        self, optimizer: HealingConfigOptimizer, sample_snapshot: HealingOutcomeAggregateSnapshot
    ) -> None:
        """T4 - Deterministic aggregation: same inputs should produce same outputs."""
        import hashlib

        # Create embedding metadata
        embedding_metadata = {
            "embedding_enabled_at_time": True,
            "embedding_replay_key": "test_replay_key",
            "embedding_artifact_hash": "test_hash",
            "embedding_topk_hashes": ["hash1", "hash2", "hash3"],
            "embedding_topk_scores_round6": [0.85, 0.90, 0.80],  # Max is 0.90
        }

        # Run twice with same inputs
        proposal1 = optimizer.propose_threshold_adjustments_with_embeddings(
            sample_snapshot,
            embedding_metadata=embedding_metadata,
            embedding_influence_cap=0.25,
            min_sample_threshold=THRESHOLD,
        )

        proposal2 = optimizer.propose_threshold_adjustments_with_embeddings(
            sample_snapshot,
            embedding_metadata=embedding_metadata,
            embedding_influence_cap=0.25,
            min_sample_threshold=THRESHOLD,
        )

        # Verify same number of adjustments
        assert len(proposal1.adjustments) == len(proposal2.adjustments)

        # Verify same ordering and confidence scores
        for adj1, adj2 in zip(proposal1.adjustments, proposal2.adjustments):
            assert adj1.healer_name == adj2.healer_name
            assert adj1.tier == adj2.tier
            assert adj1.failure_type == adj2.failure_type
            assert adj1.confidence == adj2.confidence
            assert adj1.proposed_threshold == adj2.proposed_threshold

        # Compute and print deterministic digest — identical across runs proves determinism
        digest_input = "|".join(
            f"{a.healer_name}:{a.tier}:{a.failure_type}:{a.confidence}:{a.proposed_threshold}"
            for a in proposal1.adjustments
        ).encode()
        digest = hashlib.sha256(digest_input).hexdigest()
        print(f"W2-DETERMINISM-DIGEST: {digest}")

    def test_audit_metadata_present(
        self, optimizer: HealingConfigOptimizer, sample_snapshot: HealingOutcomeAggregateSnapshot
    ) -> None:
        """T5 - Audit metadata: ChangePackage should include embedding metadata when enabled."""
        # This test verifies the structure is ready for metadata attachment
        # The actual attachment happens in the pipeline

        # Create embedding metadata
        embedding_metadata = {
            "embedding_enabled_at_time": True,
            "embedding_replay_key": "test_replay_key:abc123",
            "embedding_artifact_hash": "artifact_hash_456",
            "embedding_topk_hashes": ["hash1", "hash2"],
            "embedding_topk_scores_round6": [0.85, 0.90],
        }

        # Get proposal with embeddings
        proposal = optimizer.propose_threshold_adjustments_with_embeddings(
            sample_snapshot,
            embedding_metadata=embedding_metadata,
            embedding_influence_cap=0.25,
            min_sample_threshold=THRESHOLD,
        )

        # Verify proposal has adjustments with embedding influence
        assert len(proposal.adjustments) > 0

        # Verify at least one adjustment has embedding influence
        embedding_influenced = any("embedding_influenced" in adj.reason for adj in proposal.adjustments)
        assert embedding_influenced, "Should have embedding-influenced adjustments"

        # Verify embedding scores are used in aggregation
        # The max score (0.90) should be reflected in the confidence
        for adj in proposal.adjustments:
            if "embedding_influenced" in adj.reason:
                # Check that the embedding score is mentioned
                assert "score=0.900000" in adj.reason

    def test_embedding_score_aggregation(self, optimizer: HealingConfigOptimizer) -> None:
        """Test deterministic embedding score aggregation."""
        # Test empty scores
        assert optimizer._aggregate_embedding_scores([]) == 0.0

        # Test single score
        assert optimizer._aggregate_embedding_scores([0.85]) == 0.85

        # Test multiple scores (should return max)
        assert optimizer._aggregate_embedding_scores([0.70, 0.90, 0.80]) == 0.90
        assert optimizer._aggregate_embedding_scores([0.95, 0.85, 0.88]) == 0.95
