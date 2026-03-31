"""Test BGE embedding types functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestBgeEmbeddingTypes:
    """Test BGE embedding types functionality."""

    def test_bge_types_imports(self):
        """Test BGE types module imports."""
        from system_learning.embedding import types
        assert types is not None

    def test_embedding_vector_type(self):
        """Test embedding vector type exists."""
        from system_learning.embedding.types import EmbeddingVector
        assert EmbeddingVector is not None

    def test_embedding_metadata_type(self):
        """Test embedding metadata type exists."""
        from system_learning.embedding.types import EmbeddingMetadata
        assert EmbeddingMetadata is not None
