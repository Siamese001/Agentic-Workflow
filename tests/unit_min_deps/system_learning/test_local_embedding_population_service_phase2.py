"""Phase 2 contract tests for LocalEmbeddingPopulationService.

Tests deterministic pipeline, hash reproducibility, ordering invariance,
and search stability using in-memory fallback without faiss.
"""

import hashlib
import json
import math
import tempfile
from pathlib import Path

import pytest

from system_learning.engines.local_embedding_population_service import (
    LocalEmbeddingPopulationService,
    extract_embedding_text,
    normalize_l2,
)
from system_learning.engines.local_faiss_store import LocalFAISSStore


class FakeEmbedder:
    """Public fake embedder for testing - deterministic mapping from text to vector."""

    def embed_batch(self, texts, dimension):
        """Generate deterministic vectors from text using SHA-256."""
        out = []
        for text in texts:
            # Use SHA-256 of text to generate deterministic vector
            h = hashlib.sha256(text.encode("utf-8")).digest()
            # Map bytes to float values in [0, 1]
            v = [(h[i % 32] / 255.0) for i in range(dimension)]
            out.append(v)
        return out


pytestmark = pytest.mark.unit_min_deps


def test_collect_only_inventory_exists():
    """Test 1: collect-only inventory exists and is discoverable."""
    # This test passes if the module is imported successfully
    assert LocalEmbeddingPopulationService is not None
    assert FakeEmbedder is not None


def test_determinism_hash_reproducibility():
    """Test 2: same corpus + same built_at_utc + same embedder -> identical hash."""
    # Create temporary directory and test data
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # Create test JSONL file
        test_file = tmp_path / "test.jsonl"
        test_data = [
            {"text": "alpha", "trace_id": "t1", "content_hash": "c1"},
            {"text": "beta", "trace_id": "t2", "content_hash": "c2"},
        ]
        test_file.write_text("\n".join(json.dumps(record) for record in test_data), encoding="utf-8")

        # Setup service and store
        store = LocalFAISSStore(base_path=tmp_path)
        embedder = FakeEmbedder()
        service = LocalEmbeddingPopulationService(
            faiss_store=store,
            embedder=embedder,
            canonicalization_version="canon-v1",
            embedding_model_version="emb-v1",
            embedding_model_checksum="0" * 64,
            build_seed=42,
        )

        # Build index twice with same parameters
        metadata1 = service.populate_from_jsonl(
            index_id="test_index",
            source_files=[test_file],
            dimension=8,
            built_at_utc=1234567890,
        )

        metadata2 = service.populate_from_jsonl(
            index_id="test_index",
            source_files=[test_file],
            dimension=8,
            built_at_utc=1234567890,
        )

        # Hashes should be identical
        assert metadata1.index_version_hash == metadata2.index_version_hash
        assert len(metadata1.index_version_hash) == 64  # SHA-256 hex
        assert all(c in "0123456789abcdef" for c in metadata1.index_version_hash)


def test_ordering_invariance():
    """Test 3: permuting input file order yields identical index_version_hash."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # Create multiple test files
        file1 = tmp_path / "file1.jsonl"
        file2 = tmp_path / "file2.jsonl"

        file1.write_text(json.dumps({"text": "first", "trace_id": "t1", "content_hash": "c1"}) + "\n")
        file2.write_text(json.dumps({"text": "second", "trace_id": "t2", "content_hash": "c2"}) + "\n")

        # Setup service and store
        store = LocalFAISSStore(base_path=tmp_path)
        embedder = FakeEmbedder()
        service = LocalEmbeddingPopulationService(
            faiss_store=store,
            embedder=embedder,
            canonicalization_version="canon-v1",
            embedding_model_version="emb-v1",
            embedding_model_checksum="0" * 64,
            build_seed=42,
        )

        # Build with file1, then file2
        metadata1 = service.populate_from_jsonl(
            index_id="test_index",
            source_files=[file1, file2],
            dimension=8,
            built_at_utc=1234567890,
        )

        # Build with file2, then file1 (different order)
        metadata2 = service.populate_from_jsonl(
            index_id="test_index",
            source_files=[file2, file1],
            dimension=8,
            built_at_utc=1234567890,
        )

        # Hashes should be identical despite file order difference
        assert metadata1.index_version_hash == metadata2.index_version_hash


def test_search_stability():
    """Test 4: fixed query returns deterministic results with required post-sort tiebreak."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # Create test data with known vectors
        test_file = tmp_path / "test.jsonl"
        test_data = [
            {"text": "alpha", "trace_id": "t1", "content_hash": "c1"},
            {"text": "beta", "trace_id": "t2", "content_hash": "c2"},
            {"text": "gamma", "trace_id": "t3", "content_hash": "c3"},
        ]
        test_file.write_text("\n".join(json.dumps(record) for record in test_data), encoding="utf-8")

        # Setup service and store
        store = LocalFAISSStore(base_path=tmp_path)
        embedder = FakeEmbedder()
        service = LocalEmbeddingPopulationService(
            faiss_store=store,
            embedder=embedder,
            canonicalization_version="canon-v1",
            embedding_model_version="emb-v1",
            embedding_model_checksum="0" * 64,
            build_seed=42,
        )

        # Build index
        service.populate_from_jsonl(
            index_id="test_index",
            source_files=[test_file],
            dimension=8,
            built_at_utc=1234567890,
        )

        # Search with fixed query
        query_vector = [1.0] * 8
        results = store.search(
            index_id="test_index",
            query_vector=query_vector,
            top_k=2,
            cutoff=0.0,
        )

        # Verify search results
        assert len(results) == 2
        assert len(results[0]) == 3  # (content_hash, trace_id, score)

        # Results should be sorted by score DESC, then content_hash ASC
        scores = [r[2] for r in results]
        assert scores == sorted(scores, reverse=True)  # Descending order

        # If scores are equal (unlikely but possible), content_hash should be ASC
        if len(set(scores)) < len(scores):
            for i in range(len(scores) - 1):
                if scores[i] == scores[i + 1]:
                    assert results[i][0] <= results[i + 1][0]  # content_hash ASC


def test_extract_embedding_text():
    """Test extract_embedding_text function."""
    # Valid record
    record = {"text": "hello world", "other": "data"}
    assert extract_embedding_text(record) == "hello world"

    # Missing text field
    with pytest.raises(ValueError, match="missing required 'text' field"):
        extract_embedding_text({"other": "data"})

    # Non-string text field
    with pytest.raises(ValueError, match="'text' field must be string"):
        extract_embedding_text({"text": 123})


def test_normalize_l2():
    """Test normalize_l2 function."""
    # Normal vector
    vec = [0.6, 0.8]  # Already normalized (sqrt(0.36 + 0.64) = 1.0)
    normalized = normalize_l2(vec)
    assert math.isclose(normalized[0], 0.6, rel_tol=1e-9)
    assert math.isclose(normalized[1], 0.8, rel_tol=1e-9)

    # Non-normalized vector
    vec = [3.0, 4.0]  # Norm = 5.0
    normalized = normalize_l2(vec)
    assert math.isclose(normalized[0], 0.6, rel_tol=1e-9)
    assert math.isclose(normalized[1], 0.8, rel_tol=1e-9)

    # Zero vector (should remain unchanged)
    vec = [0.0, 0.0]
    normalized = normalize_l2(vec)
    assert normalized == [0.0, 0.0]
