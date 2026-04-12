"""Test RedisCacheClient functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRedisCacheClient:
    """Test RedisCacheClient functionality."""

    def test_redis_cache_client_imports(self):
        """Test redis_cache_client module imports."""
        from agentic_core import redis_cache_client

        assert redis_cache_client is not None

    def test_redis_cache_client_class(self):
        """Test RedisCacheClient class exists."""
        from agentic_core import RedisCacheClient

        assert RedisCacheClient is not None

    def test_redis_cache_client_callable(self):
        """Test redis_cache_client functions are callable."""
        from agentic_core import validate_redis_cache_client

        assert callable(validate_redis_cache_client)
