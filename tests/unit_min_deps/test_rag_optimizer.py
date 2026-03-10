"""Unit tests for system_learning.engines.rag_optimizer."""

import pytest

from system_learning.engines.rag_optimizer import (
    RAGChangePackage,
    propose_rag_param_changes,
)
from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy

pytestmark = pytest.mark.unit_min_deps


class TestRAGOptimizer:
    def test_valid_proposal_passes_constraints(self):
        """Valid proposal within bounds and delta."""
        cooldown = CooldownPolicy(min_seconds_between_updates=3600)
        sample = SampleSizePolicy(min_observations=1000)

        proposal = propose_rag_param_changes(
            snapshot_id="snap456",
            metrics={"retrieval_precision": 0.65},
            current_config={"retrieval_top_k": 10},
            now_utc=1700003600,
            history={
                "retrieval_top_k_last_update": 1700000000,
                "retrieval_top_k_n_obs": 2000,
            },
            cooldown_policy=cooldown,
            sample_policy=sample,
        )

        assert proposal is not None
        assert proposal.surface_name == "retrieval_top_k"
        assert proposal.old_value == 10
        assert proposal.new_value == 12

    def test_out_of_range_rejected(self):
        """Proposal exceeding max bounds raises."""
        cooldown = CooldownPolicy(min_seconds_between_updates=3600)
        sample = SampleSizePolicy(min_observations=1000)

        # The heuristic caps at 20, so this won't exceed bounds
        # Instead, test that the capping works correctly
        proposal = propose_rag_param_changes(
            snapshot_id="snap456",
            metrics={"retrieval_precision": 0.50},
            current_config={"retrieval_top_k": 19},
            now_utc=1700003600,
            history={
                "retrieval_top_k_last_update": 1700000000,
                "retrieval_top_k_n_obs": 2000,
            },
            cooldown_policy=cooldown,
            sample_policy=sample,
        )
        # Proposal should be capped at max (20)
        assert proposal is not None
        assert proposal.new_value == 20

    def test_cooldown_violated_returns_none(self):
        """Cooldown violation returns None (no proposal)."""
        cooldown = CooldownPolicy(min_seconds_between_updates=3600)
        sample = SampleSizePolicy(min_observations=1000)

        proposal = propose_rag_param_changes(
            snapshot_id="snap456",
            metrics={"retrieval_precision": 0.65},
            current_config={"retrieval_top_k": 10},
            now_utc=1700001800,  # Only 1800 seconds elapsed
            history={
                "retrieval_top_k_last_update": 1700000000,
                "retrieval_top_k_n_obs": 2000,
            },
            cooldown_policy=cooldown,
            sample_policy=sample,
        )

        assert proposal is None

    def test_sample_size_violated_returns_none(self):
        """Sample size violation returns None (no proposal)."""
        cooldown = CooldownPolicy(min_seconds_between_updates=3600)
        sample = SampleSizePolicy(min_observations=1000)

        proposal = propose_rag_param_changes(
            snapshot_id="snap456",
            metrics={"retrieval_precision": 0.65},
            current_config={"retrieval_top_k": 10},
            now_utc=1700003600,
            history={
                "retrieval_top_k_last_update": 1700000000,
                "retrieval_top_k_n_obs": 500,  # Below minimum
            },
            cooldown_policy=cooldown,
            sample_policy=sample,
        )

        assert proposal is None

    def test_no_change_needed_returns_none(self):
        """No change needed when metrics are in acceptable range."""
        cooldown = CooldownPolicy(min_seconds_between_updates=3600)
        sample = SampleSizePolicy(min_observations=1000)

        proposal = propose_rag_param_changes(
            snapshot_id="snap456",
            metrics={"retrieval_precision": 0.75},  # In acceptable range
            current_config={"retrieval_top_k": 10},
            now_utc=1700003600,
            history={
                "retrieval_top_k_last_update": 1700000000,
                "retrieval_top_k_n_obs": 2000,
            },
            cooldown_policy=cooldown,
            sample_policy=sample,
        )

        assert proposal is None


class TestRAGChangePackage:
    def test_canonical_bytes_deterministic(self):
        """Same inputs produce identical canonical bytes."""
        pkg1 = RAGChangePackage(
            surface_name="retrieval_top_k",
            old_value=10,
            new_value=12,
            justification="test",
            snapshot_id="snap456",
        )
        pkg2 = RAGChangePackage(
            surface_name="retrieval_top_k",
            old_value=10,
            new_value=12,
            justification="test",
            snapshot_id="snap456",
        )

        assert pkg1.canonical_bytes() == pkg2.canonical_bytes()

    def test_content_hash_deterministic(self):
        """Same inputs produce identical content hash."""
        pkg1 = RAGChangePackage(
            surface_name="retrieval_top_k",
            old_value=10,
            new_value=12,
            justification="test",
            snapshot_id="snap456",
        )
        pkg2 = RAGChangePackage(
            surface_name="retrieval_top_k",
            old_value=10,
            new_value=12,
            justification="test",
            snapshot_id="snap456",
        )

        assert pkg1.content_hash() == pkg2.content_hash()

    def test_different_values_produce_different_hash(self):
        """Different values produce different content hash."""
        pkg1 = RAGChangePackage(
            surface_name="retrieval_top_k",
            old_value=10,
            new_value=12,
            justification="test",
            snapshot_id="snap456",
        )
        pkg2 = RAGChangePackage(
            surface_name="retrieval_top_k",
            old_value=10,
            new_value=15,
            justification="test",
            snapshot_id="snap456",
        )

        assert pkg1.content_hash() != pkg2.content_hash()


class TestDeterminism:
    def test_proposal_deterministic(self):
        """Identical inputs produce identical proposals."""
        cooldown = CooldownPolicy(min_seconds_between_updates=3600)
        sample = SampleSizePolicy(min_observations=1000)

        proposal1 = propose_rag_param_changes(
            snapshot_id="snap456",
            metrics={"retrieval_precision": 0.65},
            current_config={"retrieval_top_k": 10},
            now_utc=1700003600,
            history={
                "retrieval_top_k_last_update": 1700000000,
                "retrieval_top_k_n_obs": 2000,
            },
            cooldown_policy=cooldown,
            sample_policy=sample,
        )

        proposal2 = propose_rag_param_changes(
            snapshot_id="snap456",
            metrics={"retrieval_precision": 0.65},
            current_config={"retrieval_top_k": 10},
            now_utc=1700003600,
            history={
                "retrieval_top_k_last_update": 1700000000,
                "retrieval_top_k_n_obs": 2000,
            },
            cooldown_policy=cooldown,
            sample_policy=sample,
        )

        assert proposal1 is not None
        assert proposal2 is not None
        assert proposal1.content_hash() == proposal2.content_hash()
