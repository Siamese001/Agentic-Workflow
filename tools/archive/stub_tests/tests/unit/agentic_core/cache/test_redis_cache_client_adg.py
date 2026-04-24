"""Test RedisCacheClientAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRedisCacheClientAdg:
    """Test RedisCacheClientAdg functionality."""

    def test_redis_cache_client_adg_imports(self):
        """Test redis_cache_client_adg module imports."""
        from agentic_core import redis_cache_client_adg

        assert redis_cache_client_adg is not None

    def test_redis_cache_client_adg_class(self):
        """Test RedisCacheClientAdg class exists."""
        from agentic_core import RedisCacheClientAdg

        assert RedisCacheClientAdg is not None

    def test_redis_cache_client_adg_callable(self):
        """Test redis_cache_client_adg functions are callable."""
        from agentic_core import validate_redis_cache_client_adg

        assert callable(validate_redis_cache_client_adg)
