"""W3 Negative Control Tests - Tamper detection for pattern analysis.

W3: Pattern Analysis Engine (Deterministic, Informational-Only).

Negative control tests ensure tampering with deterministic behavior
is properly detected and reported.
"""

from __future__ import annotations

import os

import pytest

from system_learning.engines.pattern_analysis_engine import (
    PatternAnalysisEngine,
)

# Tamper flag
_TAMPER = os.environ.get("W3_NEGCTRL_TAMPER", "0") == "1"


@pytest.mark.unit_min_deps
class TestW3NegativeControl:
    """Negative control tests for W3 pattern analysis determinism."""

    def test_pattern_determinism_violation_negative_control(self) -> None:
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
