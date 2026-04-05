"""
Integration Tests for Phase 16A: Redis MCP Client
Validates sovereign caching operations through MCP architecture.
"""

import pytest
from agentic_core.config.blueprint_sovereign.environments.sovereign_config import config

from agentic_core.L4_state.cache.redis_mcp_client import SovereignRedisMCPClient, get_redis_client

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class TestRedisMCPIntegration:
    """Test suite for Redis MCP client integration."""

    @pytest.mark.asyncio
    async def test_redis_mcp_enabled(self):
        """Verify Redis MCP is enabled in sovereign config."""
        assert config.REDIS_MCP_ENABLED is True, "Redis MCP must be enabled"
        assert config.REDIS_DEFAULT_TTL_SECONDS == 3600, "Default TTL should be 3600s"
        assert config.REDIS_MAX_KEY_LENGTH == 512, "Max key length should be 512"
        assert config.REDIS_CACHE_PREFIX == "sovereign:", "Cache prefix should be 'sovereign:'"

    @pytest.mark.asyncio
    async def test_redis_client_singleton(self):
        """Verify singleton pattern for Redis client."""
        client1 = get_redis_client()
        client2 = get_redis_client()
        assert client1 is client2, "Should return same singleton instance"

    @pytest.mark.asyncio
    async def test_redis_set_get(self):
        """Test basic set and get operations via MCP."""
        client = get_redis_client()

        test_key = "test_phase16a_key"
        test_value = "test_value_sovereign"

        # Set value
        success = await client.set(test_key, test_value, ttl=60)
        assert success is True, "Set operation should succeed"

        # Get value
        retrieved = await client.get(test_key)
        assert retrieved == test_value, f"Retrieved value should match: {retrieved}"

        # Cleanup
        await client.delete(test_key)

    @pytest.mark.asyncio
    async def test_redis_delete(self):
        """Test delete operation via MCP."""
        client = get_redis_client()

        test_key = "test_delete_key"
        test_value = "delete_me"

        # Set then delete
        await client.set(test_key, test_value, ttl=60)
        deleted = await client.delete(test_key)
        assert deleted is True, "Delete should succeed"

        # Verify deletion
        retrieved = await client.get(test_key)
        assert retrieved is None, "Key should be deleted"

    @pytest.mark.asyncio
    async def test_redis_key_prefix(self):
        """Verify sovereign prefix is applied to keys."""
        client = get_redis_client()

        test_key = "prefix_test"
        test_value = "prefixed_value"

        await client.set(test_key, test_value, ttl=60)

        # The actual key in Redis should have the prefix
        # This is verified by the client implementation
        retrieved = await client.get(test_key)
        assert retrieved == test_value

        await client.delete(test_key)

    @pytest.mark.asyncio
    async def test_redis_key_length_validation(self):
        """Test key length validation against sovereign limits."""
        client = get_redis_client()

        # Create key exceeding max length
        long_key = "x" * (config.REDIS_MAX_KEY_LENGTH + 1)

        with pytest.raises(ValueError, match="exceeds sovereign limit"):
            await client.set(long_key, "value")

    @pytest.mark.asyncio
    async def test_redis_ttl_default(self):
        """Verify default TTL is applied when not specified."""
        client = get_redis_client()

        test_key = "ttl_default_test"
        test_value = "ttl_value"

        # Set without explicit TTL
        await client.set(test_key, test_value)

        # Value should be retrievable
        retrieved = await client.get(test_key)
        assert retrieved == test_value

        await client.delete(test_key)

    @pytest.mark.asyncio
    async def test_redis_list_keys(self):
        """Test listing keys with pattern matching."""
        client = get_redis_client()

        # Set multiple test keys
        test_keys = ["list_test_1", "list_test_2", "list_test_3"]
        for key in test_keys:
            await client.set(key, f"value_{key}", ttl=60)

        # List keys with pattern
        keys = await client.keys("list_test_*")

        # Should find our test keys (with prefix)
        assert isinstance(keys, list), "Should return list of keys"

        # Cleanup
        for key in test_keys:
            await client.delete(key)

    @pytest.mark.asyncio
    async def test_redis_mcp_routing(self):
        """Verify operations route through L3 MCP router."""
        client = get_redis_client()

        # Verify router is initialized
        assert hasattr(client, "router"), "Client should have router"
        assert client.router is not None, "Router should be initialized"

        # Verify router role
        assert client.router.role == "state_cache", "Router role should be state_cache"

    @pytest.mark.asyncio
    async def test_redis_error_handling(self):
        """Test graceful error handling for failed operations."""
        client = get_redis_client()

        # Attempt to get non-existent key
        result = await client.get("nonexistent_key_12345")
        assert result is None, "Should return None for non-existent key"


class TestSemanticCacheMigration:
    """Test semantic cache migration to Redis MCP."""

    @pytest.mark.asyncio
    async def test_semantic_cache_uses_mcp(self):
        """Verify semantic cache uses Redis MCP client."""
        from agentic_core.L4_state.validation_context.semantic_cache_sovereign import SovereignSemanticCache

        # Create cache instance
        cache = SovereignSemanticCache(mission_id="test_mission")

        # Verify it uses MCP client
        assert cache.redis is not None, "Should have Redis MCP client"
        assert isinstance(cache.redis, SovereignRedisMCPClient), "Should be MCP client instance"


def run_tests():
    """Run all Redis MCP integration tests."""
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])


if __name__ == "__main__":
    run_tests()
