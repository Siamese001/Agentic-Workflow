"""Test KvCacheHeadroomUnderConcurrency functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestKvCacheHeadroomUnderConcurrency:
    """Test KvCacheHeadroomUnderConcurrency functionality."""

    def test_kv_cache_headroom_under_concurrency_imports(self):
        """Test kv_cache_headroom_under_concurrency module imports."""
        from agentic_core import kv_cache_headroom_under_concurrency

        assert kv_cache_headroom_under_concurrency is not None

    def test_kv_cache_headroom_under_concurrency_class(self):
        """Test KvCacheHeadroomUnderConcurrency class exists."""
        from agentic_core import KvCacheHeadroomUnderConcurrency

        assert KvCacheHeadroomUnderConcurrency is not None

    def test_kv_cache_headroom_under_concurrency_callable(self):
        """Test kv_cache_headroom_under_concurrency functions are callable."""
        from agentic_core import validate_kv_cache_headroom_under_concurrency

        assert callable(validate_kv_cache_headroom_under_concurrency)
