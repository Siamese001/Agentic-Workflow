"""W2 negative control test - intentionally breaks determinism guard."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch

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
class TestW2NegativeControl:
    """W2 negative control tests that intentionally break guards."""

    def test_embedding_determinism_violation_negative_control(self) -> None:
        """Negative control: Break embedding score aggregation determinism."""
        # Create optimizer
        optimizer = HealingConfigOptimizer(
            min_sample_size=20,
            low_success_rate_threshold=0.5,
            escalation_delta=0.1,
            max_threshold=2.0,
            max_delta=0.2,
        )

        # Create snapshot
        aggregates = [
            (
                HealingOutcomeAggregateKey(
                    healer_name="test_healer", tier="LOCAL_AGENT", failure_type="test_failure"
                ),
                HealingOutcomeAggregate(
                    success_count=8,
                    failure_count=12,
                    total_count=20,
                ),
            ),
        ]

        snapshot = HealingOutcomeAggregateSnapshot(
            version_id="test_version",
            created_utc=1234567890,
            aggregates=tuple(aggregates),
        )

        # Create embedding metadata
        embedding_metadata = {
            "embedding_enabled_at_time": True,
            "embedding_replay_key": "test_replay_key",
            "embedding_artifact_hash": "test_hash",
            "embedding_topk_hashes": ["hash1", "hash2"],
            "embedding_topk_scores_round6": [0.85, 0.90],
        }

        # Mock _aggregate_embedding_scores to be non-deterministic
        with patch.object(optimizer, '_aggregate_embedding_scores') as mock_agg:
            # First call returns 0.90, second call returns 0.85 (non-deterministic)
            mock_agg.side_effect = [0.90, 0.85]

            # Run twice with same inputs
            proposal1 = optimizer.propose_threshold_adjustments_with_embeddings(
                snapshot,
                embedding_metadata=embedding_metadata,
                embedding_influence_cap=0.25,
                min_sample_threshold=20,
            )

            proposal2 = optimizer.propose_threshold_adjustments_with_embeddings(
                snapshot,
                embedding_metadata=embedding_metadata,
                embedding_influence_cap=0.25,
                min_sample_threshold=20,
            )

            # Assert non-deterministic behavior (different confidence scores)
            assert proposal1.adjustments[0].confidence != proposal2.adjustments[0].confidence, \
                "Negative control: Should demonstrate non-deterministic embedding scoring"

            # Verify the mock was called twice with different side effects
            assert mock_agg.call_count == 2
            assert mock_agg.call_args_list[0] == mock_agg.call_args_list[1], \
                "Same inputs but different outputs due to intentional non-determinism"

    def test_small_n_guard_violation_negative_control(self) -> None:
        """Negative control: Bypass small-N guard and assert violation."""
        # Create optimizer
        optimizer = HealingConfigOptimizer(
            min_sample_size=20,
            low_success_rate_threshold=0.5,
            escalation_delta=0.1,
            max_threshold=2.0,
            max_delta=0.2,
        )

        # Create small snapshot (below threshold)
        aggregates = [
            (
                HealingOutcomeAggregateKey(
                    healer_name="test_healer", tier="LOCAL_AGENT", failure_type="test_failure"
                ),
                HealingOutcomeAggregate(
                    success_count=0,
                    failure_count=2,
                    total_count=2,  # Below min_sample_size
                ),
            ),
        ]

        snapshot = HealingOutcomeAggregateSnapshot(
            version_id="test_version",
            created_utc=1234567890,
            aggregates=tuple(aggregates),
        )

        # Create embedding metadata
        embedding_metadata = {
            "embedding_enabled_at_time": True,
            "embedding_replay_key": "test_replay_key",
            "embedding_artifact_hash": "test_hash",
            "embedding_topk_hashes": ["hash1", "hash2"],
            "embedding_topk_scores_round6": [0.95, 0.90],
        }

        # Mock the base propose_threshold_adjustments to bypass small-N filter
        with patch.object(optimizer, 'propose_threshold_adjustments') as mock_base:
            # Create a fake adjustment that should be filtered out
            from system_learning.engines.healing_config_optimizer import ThresholdAdjustment
            fake_adjustment = ThresholdAdjustment(
                healer_name="test_healer",
                tier="LOCAL_AGENT",
                failure_type="test_failure",
                current_threshold=1.0,
                proposed_threshold=1.2,
                confidence=0.8,
                reason="embedding_influenced, weight=0.25, score=0.950000",
            )

            mock_proposal = MagicMock()
            mock_proposal.adjustments = [fake_adjustment]
            mock_base.return_value = mock_proposal

            # Run with embeddings - should bypass small-N guard due to mocking
            proposal = optimizer.propose_threshold_adjustments_with_embeddings(
                snapshot,
                embedding_metadata=embedding_metadata,
                embedding_influence_cap=0.25,
                min_sample_threshold=20,
            )

            # Assert violation: small-N guard was bypassed
            assert len(proposal.adjustments) > 0, \
                "Negative control: Should demonstrate small-N guard violation"

            # Verify embedding influence is present despite small sample size
            adj = proposal.adjustments[0]
            assert "embedding_influenced" in adj.reason, \
                "Negative control: Should have embedding influence despite small-N"
            assert "weight=0.25" in adj.reason, \
                "Negative control: Should show embedding weight"
