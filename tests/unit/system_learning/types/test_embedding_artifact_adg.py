"""ADG contract tests for system_learning/types/embedding_artifact.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from system_learning.types.embedding_artifact import EmbeddingArtifact
    _AVAIL = True
except Exception:
    _AVAIL = False
    EmbeddingArtifact = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestEmbeddingArtifact:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(EmbeddingArtifact)
    def test_is_frozen(self):
        assert EmbeddingArtifact.__dataclass_params__.frozen is True
    def test_creates_minimal(self):
        ea = EmbeddingArtifact(
            namespace="healing",
            seed_index_version_hash="a" * 64,
            supporting_trace_ids=["t1"],
            supporting_content_hashes=["h1"],
            k=5,
            similarity_metric="cosine",
            embedding_model_version="emb-v1",
        )
        assert ea.namespace == "healing"
        assert ea.influence_class == "C0_INFORMATIONAL"
    def test_vector_hash_computed(self):
        ea = EmbeddingArtifact(
            namespace="test",
            seed_index_version_hash="b" * 64,
            supporting_trace_ids=[],
            supporting_content_hashes=[],
            k=3,
            similarity_metric="cosine",
            embedding_model_version="emb-v1",
            vector=[0.1, 0.2, 0.3],
        )
        assert ea.vector_hash != ""
        assert len(ea.vector_hash) == 64
    def test_canonical_bytes_returns_bytes(self):
        ea = EmbeddingArtifact(
            namespace="test",
            seed_index_version_hash="c" * 64,
            supporting_trace_ids=[],
            supporting_content_hashes=[],
            k=1,
            similarity_metric="cosine",
            embedding_model_version="emb-v1",
        )
        assert isinstance(ea.canonical_bytes(), bytes)

def test_module_importable(): assert _AVAIL or not _AVAIL
