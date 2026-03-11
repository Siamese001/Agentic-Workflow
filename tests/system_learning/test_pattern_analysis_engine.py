"""Tests for W3 Pattern Analysis Engine.

W3: Pattern Analysis Engine (Deterministic, Informational-Only).

Tests ensure deterministic clustering, stable digests, and proper
handling of edge cases.
"""

from __future__ import annotations

import pytest

from system_learning.engines.pattern_analysis_engine import (
    PatternAnalysisEngine,
    PatternSummary,
)


@pytest.mark.unit_min_deps
class TestPatternAnalysisEngine:
    """Test suite for PatternAnalysisEngine."""

    def test_empty_input_returns_empty_summary(self) -> None:
        """T1: Empty input should return empty summary with deterministic digest."""
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
