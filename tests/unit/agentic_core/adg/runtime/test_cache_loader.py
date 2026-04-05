"""Test CacheLoader functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCacheLoader:
    """Test CacheLoader functionality."""

    def test_cache_loader_imports(self):
        """Test cache_loader module imports."""
        from agentic_core import cache_loader
        assert cache_loader is not None

    def test_cache_loader_class(self):
        """Test CacheLoader class exists."""
        from agentic_core import CacheLoader
        assert CacheLoader is not None

    def test_cache_loader_callable(self):
        """Test cache_loader functions are callable."""
        from agentic_core import validate_cache_loader
        assert callable(validate_cache_loader)
