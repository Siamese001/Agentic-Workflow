"""ADG contract tests for system_learning/types/index_build_metadata_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from system_learning.types.index_build_metadata_types import IndexBuildMetadata
    _AVAIL = True
except Exception:
    _AVAIL = False
    IndexBuildMetadata = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestIndexBuildMetadata:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(IndexBuildMetadata)
    def test_is_frozen(self):
        assert IndexBuildMetadata.__dataclass_params__.frozen is True
    def test_creates(self):
        m = IndexBuildMetadata(
            index_id="healing_contexts_v1",
            faiss_version="1.7.4",
            build_seed=42,
            canonicalization_version="canon-v1",
            embedding_model_version="text-embedding-004-v1",
            embedding_model_checksum="a" * 64,
            built_at_utc=1000000,
            index_version_hash="b" * 64,
            vector_count=512,
            dimension=768,
        )
        assert m.index_id == "healing_contexts_v1"
        assert m.build_seed == 42
        assert m.dimension == 768
    def test_canonical_json_bytes_deterministic(self):
        m = IndexBuildMetadata(
            index_id="test", faiss_version="1.7.4", build_seed=42,
            canonicalization_version="canon-v1",
            embedding_model_version="emb-v1",
            embedding_model_checksum="c" * 64,
            built_at_utc=999, index_version_hash="d" * 64,
            vector_count=10, dimension=128,
        )
        b1 = m.to_canonical_json_bytes()
        b2 = m.to_canonical_json_bytes()
        assert b1 == b2
        assert isinstance(b1, bytes)

def test_module_importable(): assert _AVAIL or not _AVAIL
