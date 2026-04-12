"""Test RedisMcp functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRedisMcp:
    """Test RedisMcp functionality."""

    def test_redis_mcp_imports(self):
        """Test redis_mcp module imports."""
        from agentic_core import redis_mcp

        assert redis_mcp is not None

    def test_redis_mcp_class(self):
        """Test RedisCacheClient (DeterministicRedisCache) class exists."""
        from agentic_core import RedisCacheClient

        assert RedisCacheClient is not None

    def test_redis_mcp_callable(self):
        """Test DeterministicRedisCache is instantiable (callable)."""
        from agentic_core import RedisCacheClient

        assert callable(RedisCacheClient)
