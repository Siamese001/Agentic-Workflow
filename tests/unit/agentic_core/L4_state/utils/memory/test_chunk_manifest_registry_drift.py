"""
Unit tests for ChunkManifestRegistry drift detection methods (W3-P5).

Tests for check_drift() and verify_fact_vec_hash() methods added
to detect ChromaDB <-> SQLite fact_vec drift.
"""
import hashlib
import json
import tempfile
from pathlib import Path

from agentic_core.L4_state.utils.memory.chunk_manifest_registry import (
    ChunkManifestRegistry,
    EnrichedChunkManifest,
)


class TestChunkManifestRegistryDriftDetection:
    """Test drift detection methods in ChunkManifestRegistry."""

    def test_verify_fact_vec_hash_valid(self):
        """verify_fact_vec_hash returns True for valid hash."""
        # Create a test manifest with a fact_vec
        fact_vec = [0.1, 0.2, 0.3, 0.4, 0.5]
        fact_vec_hash = hashlib.sha256(
            json.dumps(fact_vec, sort_keys=True).encode(),
        ).hexdigest()[:16]

        manifest = EnrichedChunkManifest(
            chunk_id="test_chunk_1",
            raw_content="test content",
            enriched_content={"raw": "test content"},
            title="Test",
            summary="Test summary",
            key_concepts=["test"],
            fact_vec=fact_vec,
            fact_vec_hash=fact_vec_hash,
            doc_id="doc_1",
            source_file="test.py",
            chunk_index=0,
        )

        # Create a temporary registry
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_manifests.sqlite"
            registry = ChunkManifestRegistry(db_path=str(db_path))

            result = registry.verify_fact_vec_hash(manifest)
            assert result is True

    def test_verify_fact_vec_hash_invalid(self):
        """verify_fact_vec_hash returns False for mismatched hash."""
        fact_vec = [0.1, 0.2, 0.3, 0.4, 0.5]
        wrong_hash = "wrong_hash_value"

        manifest = EnrichedChunkManifest(
            chunk_id="test_chunk_1",
            raw_content="test content",
            enriched_content={"raw": "test content"},
            title="Test",
            summary="Test summary",
            key_concepts=["test"],
            fact_vec=fact_vec,
            fact_vec_hash=wrong_hash,
            doc_id="doc_1",
            source_file="test.py",
            chunk_index=0,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_manifests.sqlite"
            registry = ChunkManifestRegistry(db_path=str(db_path))

            result = registry.verify_fact_vec_hash(manifest)
            assert result is False

    def test_verify_fact_vec_hash_no_embedding(self):
        """verify_fact_vec_hash returns True when fact_vec is None (no embedding)."""
        manifest = EnrichedChunkManifest(
            chunk_id="test_chunk_1",
            raw_content="test content",
            enriched_content={"raw": "test content"},
            title="Test",
            summary="Test summary",
            key_concepts=["test"],
            fact_vec=None,
            fact_vec_hash="",
            doc_id="doc_1",
            source_file="test.py",
            chunk_index=0,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_manifests.sqlite"
            registry = ChunkManifestRegistry(db_path=str(db_path))

            result = registry.verify_fact_vec_hash(manifest)
            assert result is True  # No embedding to verify

    def test_check_drift_no_chroma_collection(self):
        """check_drift returns empty lists when ChromaDB query fails gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_manifests.sqlite"
            registry = ChunkManifestRegistry(db_path=str(db_path))

            # Store a manifest
            manifest = EnrichedChunkManifest(
                chunk_id="test_chunk_1",
                raw_content="test content",
                enriched_content={"raw": "test content"},
                title="Test",
                summary="Test summary",
                key_concepts=["test"],
                fact_vec=[0.1, 0.2],
                fact_vec_hash="hash123",
                doc_id="doc_1",
                source_file="test.py",
                chunk_index=0,
            )
            registry.store_manifest(manifest)

            # Pass None as chroma_collection (will fail gracefully)
            result = registry.check_drift(None)
            assert result["missing_in_chroma"] == ["test_chunk_1"]
            assert result["missing_in_sqlite"] == []

    def test_check_drift_no_drift(self):
        """check_drift returns empty lists when SQLite and mock ChromaDB are in sync."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_manifests.sqlite"
            registry = ChunkManifestRegistry(db_path=str(db_path))

            # Store a manifest
            manifest = EnrichedChunkManifest(
                chunk_id="test_chunk_1",
                raw_content="test content",
                enriched_content={"raw": "test content"},
                title="Test",
                summary="Test summary",
                key_concepts=["test"],
                fact_vec=[0.1, 0.2],
                fact_vec_hash="hash123",
                doc_id="doc_1",
                source_file="test.py",
                chunk_index=0,
            )
            registry.store_manifest(manifest)

            # Mock ChromaDB collection that returns the same ID
            class MockChromaCollection:
                def get(self):
                    return {"ids": ["test_chunk_1"]}

            result = registry.check_drift(MockChromaCollection())
            assert result["missing_in_chroma"] == []
            assert result["missing_in_sqlite"] == []

    def test_check_drift_missing_in_chroma(self):
        """check_drift detects chunks in SQLite but not in ChromaDB."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_manifests.sqlite"
            registry = ChunkManifestRegistry(db_path=str(db_path))

            # Store manifests
            for i in range(3):
                manifest = EnrichedChunkManifest(
                    chunk_id=f"test_chunk_{i}",
                    raw_content=f"content {i}",
                    enriched_content={"raw": f"content {i}"},
                    title=f"Test {i}",
                    summary=f"Summary {i}",
                    key_concepts=["test"],
                    fact_vec=[0.1 * i, 0.2 * i],
                    fact_vec_hash=f"hash{i}",
                    doc_id="doc_1",
                    source_file="test.py",
                    chunk_index=i,
                )
                registry.store_manifest(manifest)

            # Mock ChromaDB collection that returns only 1 ID
            class MockChromaCollection:
                def get(self):
                    return {"ids": ["test_chunk_0"]}

            result = registry.check_drift(MockChromaCollection())
            assert set(result["missing_in_chroma"]) == {"test_chunk_1", "test_chunk_2"}
            assert result["missing_in_sqlite"] == []

    def test_check_drift_missing_in_sqlite(self):
        """check_drift detects chunks in ChromaDB but not in SQLite."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_manifests.sqlite"
            registry = ChunkManifestRegistry(db_path=str(db_path))

            # Store only 1 manifest
            manifest = EnrichedChunkManifest(
                chunk_id="test_chunk_0",
                raw_content="content 0",
                enriched_content={"raw": "content 0"},
                title="Test 0",
                summary="Summary 0",
                key_concepts=["test"],
                fact_vec=[0.1, 0.2],
                fact_vec_hash="hash0",
                doc_id="doc_1",
                source_file="test.py",
                chunk_index=0,
            )
            registry.store_manifest(manifest)

            # Mock ChromaDB collection that returns 3 IDs
            class MockChromaCollection:
                def get(self):
                    return {"ids": ["test_chunk_0", "test_chunk_1", "test_chunk_2"]}

            result = registry.check_drift(MockChromaCollection())
            assert result["missing_in_chroma"] == []
            assert set(result["missing_in_sqlite"]) == {"test_chunk_1", "test_chunk_2"}

    def test_check_drift_chroma_exception(self):
        """check_drift handles ChromaDB exceptions gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_manifests.sqlite"
            registry = ChunkManifestRegistry(db_path=str(db_path))

            # Store a manifest
            manifest = EnrichedChunkManifest(
                chunk_id="test_chunk_1",
                raw_content="test content",
                enriched_content={"raw": "test content"},
                title="Test",
                summary="Test summary",
                key_concepts=["test"],
                fact_vec=[0.1, 0.2],
                fact_vec_hash="hash123",
                doc_id="doc_1",
                source_file="test.py",
                chunk_index=0,
            )
            registry.store_manifest(manifest)

            # Mock ChromaDB collection that raises exception
            class MockChromaCollectionWithException:
                def get(self):
                    raise ConnectionError("ChromaDB connection failed")

            result = registry.check_drift(MockChromaCollectionWithException())
            assert result["missing_in_chroma"] == ["test_chunk_1"]  # Falls back to treating ChromaDB as empty
            assert result["missing_in_sqlite"] == []
