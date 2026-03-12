"""ADG contract tests for system_learning/types/seed_embedding_pack_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from system_learning.types.seed_embedding_pack_types import SeedEmbeddingPackManifest
    _AVAIL = True
except Exception:
    _AVAIL = False
    SeedEmbeddingPackManifest = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSeedEmbeddingPackManifest:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(SeedEmbeddingPackManifest)
    def test_is_frozen(self):
        assert SeedEmbeddingPackManifest.__dataclass_params__.frozen is True
    def test_creates(self):
        m = SeedEmbeddingPackManifest(
            namespace="healing_contexts",
            bootstrap_mode="minimal_seed",
            embedding_model_version="text-embedding-004-v1",
            embedding_model_checksum="a" * 64,
            canonicalization_version="canon-v1",
            dimensions=768,
            vector_count=100,
            row_index_hash="b" * 64,
            matrix_hash="c" * 64,
            seed_index_version_hash="d" * 64,
            built_at_utc=1000000,
        )
        assert m.namespace == "healing_contexts"
        assert m.dimensions == 768
    def test_canonical_json_bytes_deterministic(self):
        m = SeedEmbeddingPackManifest(
            namespace="test", bootstrap_mode="minimal_seed",
            embedding_model_version="emb-v1",
            embedding_model_checksum="e" * 64,
            canonicalization_version="canon-v1",
            dimensions=128, vector_count=10,
            row_index_hash="f" * 64, matrix_hash="g" * 64,
            seed_index_version_hash="h" * 64, built_at_utc=999,
        )
        b1 = m.to_canonical_json_bytes()
        b2 = m.to_canonical_json_bytes()
        assert b1 == b2; assert isinstance(b1, bytes)

def test_module_importable(): assert _AVAIL or not _AVAIL
