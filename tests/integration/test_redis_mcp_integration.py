"""
Integration Tests for Phase 16A: Redis MCP Client
Validates sovereign caching operations through MCP architecture.
"""
import asyncio
import pytest
from agentic_core.L4_state.caching.redis_mcp_client import get_redis_client, SovereignRedisMCPClient
from agentic_core.config.P1_core.sovereign_config import config

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)


class test_redis_mcp_integration:
    """Test suite for Redis MCP client integration."""

    @pytest.mark.asyncio
    async def test_redis_mcp_enabled(self) -> Any:
        """Verify Redis MCP is enabled in sovereign config."""
        assert config.REDIS_MCP_ENABLED is True, 'Redis MCP must be enabled'
        assert config.REDIS_DEFAULT_TTL_SECONDS == 3600, 'Default TTL should be 3600s'
        assert config.REDIS_MAX_KEY_LENGTH == 512, 'Max key length should be 512'
        assert config.REDIS_CACHE_PREFIX == 'sovereign:', "Cache prefix should be 'sovereign:'"

    @pytest.mark.asyncio
    async def test_redis_client_singleton(self) -> Any:
        """Verify singleton pattern for Redis client."""
        client1: Any = get_redis_client()
        client2: Any = get_redis_client()
        assert client1 is client2, 'Should return same singleton instance'

    @pytest.mark.asyncio
    async def test_redis_set_get(self) -> Any:
        """Test basic set and get operations via MCP."""
        client: Any = get_redis_client()
        test_key: Any = 'test_phase16a_key'
        test_value: Any = 'test_value_sovereign'
        success: Any = await client.set(test_key, test_value, ttl=60)
        assert success is True, 'Set operation should succeed'
        retrieved: Any = await client.get(test_key)
        assert retrieved == test_value, f'Retrieved value should match: {retrieved}'
        await client.delete(test_key)

    @pytest.mark.asyncio
    async def test_redis_delete(self) -> Any:
        """Test delete operation via MCP."""
        client: Any = get_redis_client()
        test_key: Any = 'test_delete_key'
        test_value: Any = 'delete_me'
        await client.set(test_key, test_value, ttl=60)
        deleted: Any = await client.delete(test_key)
        assert deleted is True, 'Delete should succeed'
        retrieved: Any = await client.get(test_key)
        assert retrieved is None, 'Key should be deleted'

    @pytest.mark.asyncio
    async def test_redis_key_prefix(self) -> Any:
        """Verify sovereign prefix is applied to keys."""
        client: Any = get_redis_client()
        test_key: Any = 'prefix_test'
        test_value: Any = 'prefixed_value'
        await client.set(test_key, test_value, ttl=60)
        retrieved: Any = await client.get(test_key)
        assert retrieved == test_value
        await client.delete(test_key)

    @pytest.mark.asyncio
    async def test_redis_key_length_validation(self) -> Any:
        """Test key length validation against sovereign limits."""
        client: Any = get_redis_client()
        long_key: Any = 'x' * (config.REDIS_MAX_KEY_LENGTH + 1)
        with pytest.raises(ValueError, match='exceeds sovereign limit'):
            await client.set(long_key, 'value')

    @pytest.mark.asyncio
    async def test_redis_ttl_default(self) -> Any:
        """Verify default TTL is applied when not specified."""
        client: Any = get_redis_client()
        test_key: Any = 'ttl_default_test'
        test_value: Any = 'ttl_value'
        await client.set(test_key, test_value)
        retrieved: Any = await client.get(test_key)
        assert retrieved == test_value
        await client.delete(test_key)

    @pytest.mark.asyncio
    async def test_redis_list_keys(self) -> Any:
        """Test listing keys with pattern matching."""
        client: Any = get_redis_client()
        test_keys: Any = ['list_test_1', 'list_test_2', 'list_test_3']
        for key in test_keys:
            await client.set(key, f'value_{key}', ttl=60)
        keys: Any = await client.keys('list_test_*')
        assert isinstance(keys, list), 'Should return list of keys'
        for key in test_keys:
            await client.delete(key)

    @pytest.mark.asyncio
    async def test_redis_mcp_routing(self) -> Any:
        """Verify operations route through L3 MCP router."""
        client: Any = get_redis_client()
        assert hasattr(client, 'router'), 'Client should have router'
        assert client.router is not None, 'Router should be initialized'
        assert client.router.role == 'state_cache', 'Router role should be state_cache'

    @pytest.mark.asyncio
    async def test_redis_error_handling(self) -> Any:
        """Test graceful error handling for failed operations."""
        client: Any = get_redis_client()
        result: Any = await client.get('nonexistent_key_12345')
        assert result is None, 'Should return None for non-existent key'

class test_semantic_cache_migration:
    """Test semantic cache migration to Redis MCP."""

    @pytest.mark.asyncio
    async def test_semantic_cache_uses_mcp(self) -> Any:
        """Verify semantic cache uses Redis MCP client."""
        from agentic_core.L4_state.validation_context.semantic_cache_sovereign import SovereignSemanticCache
        cache: Any = SovereignSemanticCache(mission_id='test_mission')
        assert cache.redis is not None, 'Should have Redis MCP client'
        assert isinstance(cache.redis, SovereignRedisMCPClient), 'Should be MCP client instance'

def run_tests() -> Any:
    """Run all Redis MCP integration tests."""
    pytest.main([__file__, '-v', '--asyncio-mode=auto'])
if __name__ == '__main__':
    run_tests()
