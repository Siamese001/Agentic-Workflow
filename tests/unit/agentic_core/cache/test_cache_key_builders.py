"""Test CacheKeyBuilders functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCacheKeyBuilders:
    """Test CacheKeyBuilders functionality."""

    def test_cache_key_builders_imports(self):
        """Test cache_key_builders module imports."""
        from agentic_core import cache_key_builders
        assert cache_key_builders is not None

    def test_cache_key_builders_class(self):
        """Test CacheKeyBuilders class exists."""
        from agentic_core import CacheKeyBuilders
        assert CacheKeyBuilders is not None

    def test_cache_key_builders_callable(self):
        """Test cache_key_builders functions are callable."""
        from agentic_core import validate_cache_key_builders
        assert callable(validate_cache_key_builders)
