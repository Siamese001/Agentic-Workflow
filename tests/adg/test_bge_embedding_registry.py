"""Test BGE embedding registry functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestBgeEmbeddingRegistry:
    """Test BGE embedding registry functionality."""

    def test_bge_registry_imports(self):
        """Test BGE registry module imports."""
        from system_learning.embedding import registry
        assert registry is not None

    def test_bge_registry_exists(self):
        """Test BGE embedding registry exists."""
        from system_learning.embedding.registry import EMBEDDING_REGISTRY
        assert isinstance(EMBEDDING_REGISTRY, dict)

    def test_bge_register_function(self):
        """Test BGE register function."""
        from system_learning.embedding.registry import register_embedder
        assert callable(register_embedder)
