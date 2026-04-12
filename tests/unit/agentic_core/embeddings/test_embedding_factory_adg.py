"""Test EmbeddingFactoryAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestEmbeddingFactoryAdg:
    """Test EmbeddingFactoryAdg functionality."""

    def test_embedding_factory_adg_imports(self):
        """Test embedding_factory_adg module imports."""
        from agentic_core import embedding_factory_adg

        assert embedding_factory_adg is not None

    def test_embedding_factory_adg_class(self):
        """Test EmbeddingFactoryAdg class exists."""
        from agentic_core import EmbeddingFactoryAdg

        assert EmbeddingFactoryAdg is not None

    def test_embedding_factory_adg_callable(self):
        """Test embedding_factory_adg functions are callable."""
        from agentic_core import validate_embedding_factory_adg

        assert callable(validate_embedding_factory_adg)
