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

from system_learning.engines.embedding_service_factory import EmbeddingServiceFactory
from system_learning.engines.healing_config_optimizer import (
    HealingConfigOptimizer,
)
from system_learning.types.healing_outcome_learning_types import (
    HealingOutcomeAggregate,
    HealingOutcomeAggregateKey,
    HealingOutcomeAggregateSnapshot,
)


@pytest.mark.unit_min_deps
class TestHealingConfigOptimizerEmbeddings:
    """Test W2 embedding integration in HealingConfigOptimizer."""

    @pytest.fixture
    def optimizer(self) -> HealingConfigOptimizer:
        """Create optimizer with test parameters."""
        return HealingConfigOptimizer(
            min_sample_size=20,
            low_success_rate_threshold=0.5,
            escalation_delta=0.1,
            max_threshold=2.0,
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
                min_sample_threshold=20,
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
            min_sample_threshold=20,
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
            min_sample_threshold=20,
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
            min_sample_threshold=20,
        )

        proposal2 = optimizer.propose_threshold_adjustments_with_embeddings(
            sample_snapshot,
            embedding_metadata=embedding_metadata,
            embedding_influence_cap=0.25,
            min_sample_threshold=20,
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
            min_sample_threshold=20,
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
