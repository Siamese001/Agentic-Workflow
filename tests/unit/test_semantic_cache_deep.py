"""Test SemanticCacheDeep functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSemanticCacheDeep:
    """Test SemanticCacheDeep functionality."""

    def test_semantic_cache_deep_imports(self):
        """Test semantic_cache_deep module imports."""
        from agentic_core import semantic_cache_deep
        assert semantic_cache_deep is not None

    def test_semantic_cache_deep_class(self):
        """Test SemanticCacheDeep class exists."""
        from agentic_core import SemanticCacheDeep
        assert SemanticCacheDeep is not None

    def test_semantic_cache_deep_callable(self):
        """Test semantic_cache_deep functions are callable."""
        from agentic_core import validate_semantic_cache_deep
        assert callable(validate_semantic_cache_deep)
