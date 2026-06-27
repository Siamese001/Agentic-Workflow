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

    def test_redis_protocol_defaults_to_resp2(self, monkeypatch):
        """Legacy local Redis 3.x does not support the HELLO/RESP3 handshake."""
        from agentic_core.cache.redis_cache_client import redis_connection_protocol_kwargs

        monkeypatch.delenv("REDIS_PROTOCOL", raising=False)
        assert redis_connection_protocol_kwargs() == {"protocol": 2}

    @pytest.mark.parametrize("raw", ["3", "2"])
    def test_redis_protocol_allows_explicit_supported_values(self, monkeypatch, raw):
        from agentic_core.cache.redis_cache_client import redis_connection_protocol_kwargs

        monkeypatch.setenv("REDIS_PROTOCOL", raw)
        assert redis_connection_protocol_kwargs() == {"protocol": int(raw)}

    @pytest.mark.parametrize("raw", ["", "1", "not-a-number"])
    def test_redis_protocol_falls_back_to_resp2_on_invalid_values(self, monkeypatch, raw):
        from agentic_core.cache.redis_cache_client import redis_connection_protocol_kwargs

        monkeypatch.setenv("REDIS_PROTOCOL", raw)
        assert redis_connection_protocol_kwargs() == {"protocol": 2}
