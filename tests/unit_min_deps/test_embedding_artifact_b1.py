"""Tests for EmbeddingArtifact type (Plan B Phase 1).

Comprehensive test suite covering determinism, canonical bytes, hash computation,
and invariants enforcement.
"""

from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from system_learning.types.embedding_artifact import EmbeddingArtifact

_emit_records_execution_trace("p0", "evidence", "test_embedding_artifact_b1")
_emit_applies_guardrail("p0", "test_embedding_artifact_b1", "p0_governance")
_emit_reads_policy_state("p0", "test_embedding_artifact_b1", "policy_binding")
_emit_snapshots_state("p0", "test_embedding_artifact_b1", "state_snapshot")
emit_replay_key("p0", "test_embedding_artifact_b1")
emit_determinism_digest("p0", "test_embedding_artifact_b1")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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


class TestEmbeddingArtifactDeterminism:
    """Test deterministic behavior of EmbeddingArtifact."""

    def test_same_inputs_identical_canonical_bytes(self):
        """Same inputs → identical canonical_bytes."""
        artifact1 = EmbeddingArtifact(
            namespace="test_namespace",
            seed_index_version_hash="abcd1234",
            supporting_trace_ids=["t3", "t1", "t2"],
            supporting_content_hashes=["h3", "h1", "h2"],
            k=10,
            similarity_metric="cosine",
            embedding_model_version="v1.0",
        )

        artifact2 = EmbeddingArtifact(
            namespace="test_namespace",
            seed_index_version_hash="abcd1234",
            supporting_trace_ids=["t3", "t1", "t2"],
            supporting_content_hashes=["h3", "h1", "h2"],
            k=10,
            similarity_metric="cosine",
            embedding_model_version="v1.0",
        )

        assert artifact1.canonical_bytes() == artifact2.canonical_bytes()

    def test_same_inputs_identical_artifact_hash(self):
        """Same inputs → identical artifact_hash."""
        artifact1 = EmbeddingArtifact(
            namespace="test_namespace",
            seed_index_version_hash="abcd1234",
            supporting_trace_ids=["t3", "t1", "t2"],
            supporting_content_hashes=["h3", "h1", "h2"],
            k=10,
            similarity_metric="cosine",
            embedding_model_version="v1.0",
        )

        artifact2 = EmbeddingArtifact(
            namespace="test_namespace",
            seed_index_version_hash="abcd1234",
            supporting_trace_ids=["t3", "t1", "t2"],
            supporting_content_hashes=["h3", "h1", "h2"],
            k=10,
            similarity_metric="cosine",
            embedding_model_version="v1.0",
        )

        assert artifact1.artifact_hash() == artifact2.artifact_hash()

    def test_different_trace_ids_different_artifact_hash(self):
        """Different trace_ids → different artifact_hash."""
        artifact1 = EmbeddingArtifact(
            namespace="test_namespace",
            seed_index_version_hash="abcd1234",
            supporting_trace_ids=["t1", "t2"],
            supporting_content_hashes=["h1", "h2"],
            k=10,
            similarity_metric="cosine",
            embedding_model_version="v1.0",
        )

        artifact2 = EmbeddingArtifact(
            namespace="test_namespace",
            seed_index_version_hash="abcd1234",
            supporting_trace_ids=["t1", "t3"],  # Different trace_id
            supporting_content_hashes=["h1", "h2"],
            k=10,
            similarity_metric="cosine",
            embedding_model_version="v1.0",
        )

        assert artifact1.artifact_hash() != artifact2.artifact_hash()

    def test_canonical_sorting_enforced_trace_ids(self):
        """Trace IDs are automatically sorted canonically."""
        # Create with unordered trace IDs
        artifact = EmbeddingArtifact(
            namespace="test_namespace",
            seed_index_version_hash="abcd1234",
            supporting_trace_ids=["z_trace", "a_trace", "m_trace"],
            supporting_content_hashes=["h1", "h2"],
            k=10,
            similarity_metric="cosine",
            embedding_model_version="v1.0",
        )

        # Should be sorted to ["a_trace", "m_trace", "z_trace"]
        assert artifact.supporting_trace_ids == ["a_trace", "m_trace", "z_trace"]

    def test_canonical_sorting_enforced_content_hashes(self):
        """Content hashes are automatically sorted canonically."""
        artifact = EmbeddingArtifact(
            namespace="test_namespace",
            seed_index_version_hash="abcd1234",
            supporting_trace_ids=["t1", "t2"],
            supporting_content_hashes=["z_hash", "a_hash", "m_hash"],
            k=10,
            similarity_metric="cosine",
            embedding_model_version="v1.0",
        )

        # Should be sorted to ["a_hash", "m_hash", "z_hash"]
        assert artifact.supporting_content_hashes == ["a_hash", "m_hash", "z_hash"]


class TestEmbeddingArtifactNegativeControl:
    """Test negative control cases to prove determinism enforcement."""

    def test_ordering_instability_without_canonical_sort_changes_hash(self):
        """Negative control: Without canonical sort, ordering changes hash.

        This test demonstrates why canonical sorting is necessary by showing
        that different input orders would produce different hashes if not
        automatically sorted.
        """
        # Create two artifacts with different input orders
        # (they will be auto-sorted, but we can verify the sorting works)
        artifact1 = EmbeddingArtifact(
            namespace="test_namespace",
            seed_index_version_hash="abcd1234",
            supporting_trace_ids=["z_trace", "a_trace"],  # Unordered input
            supporting_content_hashes=["h1", "h2"],
            k=10,
            similarity_metric="cosine",
            embedding_model_version="v1.0",
        )

        artifact2 = EmbeddingArtifact(
            namespace="test_namespace",
            seed_index_version_hash="abcd1234",
            supporting_trace_ids=["a_trace", "z_trace"],  # Different order
            supporting_content_hashes=["h1", "h2"],
            k=10,
            similarity_metric="cosine",
            embedding_model_version="v1.0",
        )

        # Both should have the same sorted order
        assert artifact1.supporting_trace_ids == ["a_trace", "z_trace"]
        assert artifact2.supporting_trace_ids == ["a_trace", "z_trace"]

        # And therefore the same hash
        assert artifact1.artifact_hash() == artifact2.artifact_hash()


class TestEmbeddingArtifactInvariants:
    """Test invariants enforcement."""

    def test_frozen_dataclass_no_mutation(self):
        """No mutation allowed (frozen dataclass)."""
        from dataclasses import FrozenInstanceError

        artifact = EmbeddingArtifact(
            namespace="test_namespace",
            seed_index_version_hash="abcd1234",
            supporting_trace_ids=["t1", "t2"],
            supporting_content_hashes=["h1", "h2"],
            k=10,
            similarity_metric="cosine",
            embedding_model_version="v1.0",
        )

        # Direct field assignment should raise FrozenInstanceError
        with pytest.raises(FrozenInstanceError):
            artifact.namespace = "modified"

        # List append should still work (lists are mutable even in frozen dataclasses)
        # This is expected behavior - the list object itself can be modified
        # but the field reference cannot be changed to a different list
        original_len = len(artifact.supporting_trace_ids)
        artifact.supporting_trace_ids.append("t3")
        assert len(artifact.supporting_trace_ids) == original_len + 1

        # But we cannot replace the list entirely
        with pytest.raises(FrozenInstanceError):
            artifact.supporting_trace_ids = ["new_list"]

    def test_canonical_bytes_utf8_minified_json(self):
        """Canonical bytes are UTF-8 minified JSON."""
        artifact = EmbeddingArtifact(
            namespace="test",
            seed_index_version_hash="hash123",
            supporting_trace_ids=["t1"],
            supporting_content_hashes=["h1"],
            k=5,
            similarity_metric="euclidean",
            embedding_model_version="v2.0",
        )

        bytes_repr = artifact.canonical_bytes()

        # Should be valid UTF-8
        bytes_repr.decode("utf-8")

        # Should be minified (no extra whitespace)
        json_str = bytes_repr.decode("utf-8")
        assert "  " not in json_str  # No double spaces
        assert "\n" not in json_str  # No newlines
        assert "\t" not in json_str  # No tabs

    def test_canonical_bytes_deterministic_key_order(self):
        """Canonical bytes have deterministic key order."""
        artifact = EmbeddingArtifact(
            namespace="test",
            seed_index_version_hash="hash123",
            supporting_trace_ids=["t1"],
            supporting_content_hashes=["h1"],
            k=5,
            similarity_metric="euclidean",
            embedding_model_version="v2.0",
        )

        bytes_repr = artifact.canonical_bytes()
        json_str = bytes_repr.decode("utf-8")

        # Keys should appear in sorted order
        expected_order = [
            "embedding_model_version",
            "k",
            "namespace",
            "seed_index_version_hash",
            "similarity_metric",
            "supporting_content_hashes",
            "supporting_trace_ids",
        ]

        # Check that keys appear in expected order
        prev_pos = -1
        for key in expected_order:
            pos = json_str.find(f'"{key}"')
            assert pos > prev_pos, f"Key {key} not in expected order"
            prev_pos = pos

    def test_artifact_hash_sha256_of_canonical_bytes(self):
        """artifact_hash is SHA-256 of canonical_bytes."""
        import hashlib

        artifact = EmbeddingArtifact(
            namespace="test",
            seed_index_version_hash="hash123",
            supporting_trace_ids=["t1"],
            supporting_content_hashes=["h1"],
            k=5,
            similarity_metric="euclidean",
            embedding_model_version="v2.0",
        )

        canonical_bytes = artifact.canonical_bytes()
        expected_hash = hashlib.sha256(canonical_bytes).hexdigest()

        assert artifact.artifact_hash() == expected_hash

    def test_no_timestamps_in_canonical_representation(self):
        """No timestamps in canonical representation."""
        artifact = EmbeddingArtifact(
            namespace="test",
            seed_index_version_hash="hash123",
            supporting_trace_ids=["t1"],
            supporting_content_hashes=["h1"],
            k=5,
            similarity_metric="euclidean",
            embedding_model_version="v2.0",
        )

        json_str = artifact.canonical_bytes().decode("utf-8")

        # Should not contain any timestamp-related fields
        assert "timestamp" not in json_str.lower()
        assert "created_at" not in json_str.lower()
        assert "updated_at" not in json_str.lower()
        assert "time" not in json_str.lower()

    def test_no_floats_stored(self):
        """No floats stored in the artifact."""
        artifact = EmbeddingArtifact(
            namespace="test",
            seed_index_version_hash="hash123",
            supporting_trace_ids=["t1"],
            supporting_content_hashes=["h1"],
            k=5,
            similarity_metric="cosine",
            embedding_model_version="v2.0",
        )

        json_str = artifact.canonical_bytes().decode("utf-8")

        # Should not contain any floating point numbers
        # (check for decimal points in numeric values)
        import re

        # Look for numbers with decimal points
        float_pattern = r":\s*\d+\.\d+"
        assert not re.search(float_pattern, json_str), "Float values found in representation"

    def test_lists_preserve_deterministic_order(self):
        """Lists are serialized in their stored (deterministic) order."""
        artifact = EmbeddingArtifact(
            namespace="test",
            seed_index_version_hash="hash123",
            supporting_trace_ids=["c", "a", "b"],  # Will be sorted to ["a", "b", "c"]
            supporting_content_hashes=["z", "x", "y"],  # Will be sorted to ["x", "y", "z"]
            k=5,
            similarity_metric="cosine",
            embedding_model_version="v2.0",
        )

        json_str = artifact.canonical_bytes().decode("utf-8")

        # Should contain the sorted lists
        assert '"supporting_trace_ids":["a","b","c"]' in json_str
        assert '"supporting_content_hashes":["x","y","z"]' in json_str
