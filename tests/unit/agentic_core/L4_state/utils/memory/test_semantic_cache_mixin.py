"""Test SemanticCacheMixin functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSemanticCacheMixin:
    """Test SemanticCacheMixin functionality."""

    def test_semantic_cache_mixin_imports(self):
        """Test semantic_cache_mixin module imports."""
        from agentic_core import semantic_cache_mixin

        assert semantic_cache_mixin is not None

    def test_semantic_cache_mixin_class(self):
        """Test SemanticCacheMixin class exists."""
        from agentic_core import SemanticCacheMixin

        assert SemanticCacheMixin is not None

    def test_semantic_cache_mixin_callable(self):
        """Test semantic_cache_mixin functions are callable."""
        from agentic_core import validate_semantic_cache_mixin

        assert callable(validate_semantic_cache_mixin)
