"""Test BGE embedding embedders functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestBgeEmbeddingEmbedders:
    """Test BGE embedding embedders functionality."""

    def test_bge_embedders_imports(self):
        """Test BGE embedders module imports."""
        from system_learning.embedding import embedders
        assert embedders is not None

    def test_bge_embedder_class_exists(self):
        """Test BGE embedder class exists."""
        from system_learning.embedding.embedders import BGEEmbedder
        assert BGEEmbedder is not None

    def test_bge_embedding_function(self):
        """Test BGE embedding function."""
        from system_learning.embedding.embedders import embed_text
        assert callable(embed_text)
