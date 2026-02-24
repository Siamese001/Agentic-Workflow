"""Phase 4 contract tests for embedding retention scheduler.

Tests prune/rebuild cycle, determinism, and invalidation enforcement.
"""

import hashlib
import json
import tempfile
from pathlib import Path

import pytest

from system_learning.engines.embedding_retention_scheduler import (
    EmbeddingRetentionScheduler,
)
from system_learning.engines.local_embedding_population_service import (
    EmbeddingProvider,
    LocalEmbeddingPopulationService,
)
from system_learning.engines.local_faiss_store import LocalFAISSStore


class FakeEmbedder:
    """Public fake embedder for testing - deterministic mapping from text to vector."""

    def embed_batch(self, texts, dimension):
        """Generate deterministic vectors from text using SHA-256."""
        out = []
        for text in texts:
            # Use SHA-256 of text to generate deterministic vector
            h = hashlib.sha256(text.encode('utf-8')).digest()
            # Map bytes to float values in [0, 1]
            v = [(h[i % 32] / 255.0) for i in range(dimension)]
            out.append(v)
        return out


pytestmark = pytest.mark.unit_min_deps


def test_collect_only_inventory_exists():
    """Test 1: collect-only inventory exists and is discoverable."""
    # This test passes if the module is imported successfully
    assert EmbeddingRetentionScheduler is not None
    assert FakeEmbedder is not None


def test_prune_blocks_open_search_until_rebuild():
    """Test 2: after prune(), open/search raises IndexNotBuiltError until rebuild() called."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # Setup store and service
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

        # Create test data
        test_file = tmp_path / "test.jsonl"
        test_data = [
            {"text": "alpha", "trace_id": "t1", "content_hash": "c1"},
            {"text": "beta", "trace_id": "t2", "content_hash": "c2"},
            {"text": "gamma", "trace_id": "t3", "content_hash": "c3"},
        ]
        test_file.write_text(
            "\n".join(json.dumps(record) for record in test_data),
            encoding="utf-8"
        )

        # Build index
        metadata = service.populate_from_jsonl(
            index_id="test_index",
            source_files=[test_file],
            dimension=8,
            built_at_utc=1234567890,
        )

        # Verify open and search work before prune
        handle, version_hash, _ = store.open("test_index")
        results = store.search("test_index", [1.0] * 8, top_k=5, cutoff=0.0)
        assert len(results) == 3

        # Prune one item
        def prune_t2(metadata):
            return metadata.get("trace_id") == "t2"

        removed = store.prune("test_index", prune_t2)
        assert removed == 1

        # After prune, open and search should fail
        with pytest.raises(Exception):  # IndexNotBuiltError
            store.open("test_index")

        with pytest.raises(Exception):  # IndexNotBuiltError
            store.search("test_index", [1.0] * 8, top_k=5, cutoff=0.0)

        # Rebuild
        new_metadata = store.rebuild(
            "test_index",
            built_at_utc=1234567891,
            canonicalization_version="canon-v1",
            embedding_model_version="emb-v1",
            embedding_model_checksum="0" * 64,
        )

        # After rebuild, open and search should work again
        handle, version_hash, _ = store.open("test_index")
        results = store.search("test_index", [1.0] * 8, top_k=5, cutoff=0.0)
        assert len(results) == 2  # Only 2 items remain

        # Verify pruned item is not in results
        trace_ids = [r[1] for r in results]
        assert "t2" not in trace_ids


def test_prune_determinism():
    """Test 3: prune+rebuild is deterministic (same inputs → same post-prune index_version_hash)."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # Setup store and service
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

        # Create test data
        test_file = tmp_path / "test.jsonl"
        test_data = [
            {"text": "alpha", "trace_id": "t1", "content_hash": "c1"},
            {"text": "beta", "trace_id": "t2", "content_hash": "c2"},
            {"text": "gamma", "trace_id": "t3", "content_hash": "c3"},
        ]
        test_file.write_text(
            "\n".join(json.dumps(record) for record in test_data),
            encoding="utf-8"
        )

        # Function to build, prune, and rebuild
        def build_prune_rebuild():
            # Build index
            service.populate_from_jsonl(
                index_id="test_index",
                source_files=[test_file],
                dimension=8,
                built_at_utc=1234567890,
            )

            # Prune exactly 1 by predicate
            def prune_t2(metadata):
                return metadata.get("trace_id") == "t2"

            removed = store.prune("test_index", prune_t2)
            assert removed == 1

            # Rebuild
            new_metadata = store.rebuild(
                "test_index",
                built_at_utc=1234567891,
                canonicalization_version="canon-v1",
                embedding_model_version="emb-v1",
                embedding_model_checksum="0" * 64,
            )

            return new_metadata

        # Run twice from same starting corpus
        metadata1 = build_prune_rebuild()

        # Reset store for second run
        store._memory_indexes.clear()
        store._rebuild_required.clear()

        metadata2 = build_prune_rebuild()

        # Hashes should be identical
        assert metadata1.index_version_hash == metadata2.index_version_hash
        assert metadata1.vector_count == metadata2.vector_count == 2

        # Verify pruned trace_id not found
        results = store.search("test_index", [1.0] * 8, top_k=5, cutoff=0.0)
        trace_ids = [r[1] for r in results]
        assert "t2" not in trace_ids


def test_telemetry_policy_rolling_window():
    """Test 4: telemetry policy wiring (rolling window)."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # Setup store and service
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

        # Create test data with created_utc timestamps
        test_file = tmp_path / "test.jsonl"
        test_data = [
            {"text": "old", "trace_id": "t1", "content_hash": "c1", "created_utc": 1000000},
            {"text": "new", "trace_id": "t2", "content_hash": "c2", "created_utc": 2000000},
            {"text": "newer", "trace_id": "t3", "content_hash": "c3", "created_utc": 3000000},
        ]
        test_file.write_text(
            "\n".join(json.dumps(record) for record in test_data),
            encoding="utf-8"
        )

        # Build index
        metadata = service.populate_from_jsonl(
            index_id="telemetry_events_v1",
            source_files=[test_file],
            dimension=8,
            built_at_utc=1234567890,
        )

        # Manually add created_utc to metadata for testing
        # In real implementation, this would come from the corpus extraction
        memory_idx = store._memory_indexes["telemetry_events_v1"]
        for i, record in enumerate(test_data):
            memory_idx["metadatas"][i]["created_utc"] = record["created_utc"]

        # Setup scheduler with rolling window policy (retention 1 day = 86400 seconds)
        scheduler = EmbeddingRetentionScheduler()
        now_utc = 2000000 + 86400  # Day after "new" timestamp

        policies = {
            "telemetry_events_v1": {
                "mode": "rolling_window",
                "retention_days": 1,
            }
        }

        stores = {"telemetry_events_v1": store}

        # Run scheduler
        results = scheduler.run_once(
            now_utc=now_utc,
            policies=policies,
            stores=stores,
        )

        # Should have pruned and rebuilt
        assert "telemetry_events_v1" in results

        # Verify only items newer than cutoff remain
        # cutoff = now_utc - 86400 = 2000000
        # So only "new" (2000000) and "newer" (3000000) should remain
        results = store.search("telemetry_events_v1", [1.0] * 8, top_k=5, cutoff=0.0)
        trace_ids = [r[1] for r in results]
        assert "t1" not in trace_ids  # "old" should be pruned
        assert "t2" in trace_ids     # "new" should remain
        assert "t3" in trace_ids     # "newer" should remain
