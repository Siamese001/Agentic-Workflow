"""
Integration tests for Redis MCP client functionality.
Tests the sovereign Redis MCP client with real MCP operations.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

from agentic_core.L4_state.caching.redis_mcp_client import SovereignRedisMCPClient, get_redis_client
from agentic_core.config.core.sovereign_config import get_sovereign_config


class TestRedisMCPIntegration:
    """Test Redis MCP client integration."""

    @pytest.fixture
    def mock_config(self):
        """Mock config with Redis MCP enabled."""
        config = MagicMock()
        config.get_bool.return_value = True
        config.get_int.return_value = 250
        config.get_str.return_value = "test:"
        return config

    @pytest.fixture
    def mock_router(self):
        """Mock MCP router."""
        router = MagicMock()
        router.manager.call_tool = AsyncMock()
        return router

    def test_get_redis_client_singleton(self):
        """Test that get_redis_client returns singleton instance."""
        # Reset singleton
        import agentic_core.L4_state.caching.redis_mcp_client as client_module
        client_module._redis_client = None

        client1 = get_redis_client()
        client2 = get_redis_client()

        assert client1 is client2

    def test_client_init_disabled(self):
        """Test client initialization fails when Redis MCP disabled."""
        config = MagicMock()
        config.get_bool.return_value = False

        with pytest.raises(ValueError, match="Redis MCP disabled"):
            SovereignRedisMCPClient()

    @pytest.mark.asyncio
    async def test_redis_get_operation(self, mock_config, mock_router):
        """Test Redis GET operation via MCP."""
        # Mock successful GET response
        mock_router.manager.call_tool.return_value = {"value": "test_value"}

        # Patch imports and config
        import agentic_core.L4_state.caching.redis_mcp_client as client_module
        original_config = client_module.get_sovereign_config
        client_module.get_sovereign_config = lambda: mock_config

        try:
            client = SovereignRedisMCPClient()
            client.router = mock_router

            result = await client.get("test_key")

            assert result == "test_value"
            mock_router.manager.call_tool.assert_called_once_with(
                "mcp9_get",
                {"key": "test:test_key"}
            )
        finally:
            client_module.get_sovereign_config = original_config

    @pytest.mark.asyncio
    async def test_redis_set_operation(self, mock_config, mock_router):
        """Test Redis SET operation via MCP."""
        # Mock successful SET response
        mock_router.manager.call_tool.return_value = {"status": "success"}

        # Patch imports and config
        import agentic_core.L4_state.caching.redis_mcp_client as client_module
        original_config = client_module.get_sovereign_config
        client_module.get_sovereign_config = lambda: mock_config

        try:
            client = SovereignRedisMCPClient()
            client.router = mock_router

            result = await client.set("test_key", "test_value", ttl=300)

            assert result is True
            mock_router.manager.call_tool.assert_called_once_with(
                "mcp9_set",
                {"key": "test:test_key", "value": "test_value", "expireSeconds": 300}
            )
        finally:
            client_module.get_sovereign_config = original_config

    @pytest.mark.asyncio
    async def test_redis_delete_operation(self, mock_config, mock_router):
        """Test Redis DELETE operation via MCP."""
        # Mock successful DELETE response
        mock_router.manager.call_tool.return_value = {"deleted": 1}

        # Patch imports and config
        import agentic_core.L4_state.caching.redis_mcp_client as client_module
        original_config = client_module.get_sovereign_config
        client_module.get_sovereign_config = lambda: mock_config

        try:
            client = SovereignRedisMCPClient()
            client.router = mock_router

            result = await client.delete("test_key")

            assert result is True
            mock_router.manager.call_tool.assert_called_once_with(
                "mcp9_delete",
                {"key": "test:test_key"}
            )
        finally:
            client_module.get_sovereign_config = original_config

    @pytest.mark.asyncio
    async def test_redis_keys_operation(self, mock_config, mock_router):
        """Test Redis KEYS operation via MCP."""
        # Mock successful KEYS response
        mock_router.manager.call_tool.return_value = {"keys": ["test:key1", "test:key2"]}

        # Patch imports and config
        import agentic_core.L4_state.caching.redis_mcp_client as client_module
        original_config = client_module.get_sovereign_config
        client_module.get_sovereign_config = lambda: mock_config

        try:
            client = SovereignRedisMCPClient()
            client.router = mock_router

            result = await client.keys("*")

            assert result == ["test:key1", "test:key2"]
            mock_router.manager.call_tool.assert_called_once_with(
                "mcp9_list",
                {"pattern": "test:*"}
            )
        finally:
            client_module.get_sovereign_config = original_config

    @pytest.mark.asyncio
    async def test_key_length_validation(self, mock_config, mock_router):
        """Test key length validation."""
        # Patch config to return small max length
        mock_config.get_int.return_value = 10

        import agentic_core.L4_state.caching.redis_mcp_client as client_module
        original_config = client_module.get_sovereign_config
        client_module.get_sovereign_config = lambda: mock_config

        try:
            client = SovereignRedisMCPClient()

            with pytest.raises(ValueError, match="Key exceeds sovereign limit"):
                await client.get("this_key_is_too_long")
        finally:
            client_module.get_sovereign_config = original_config

    @pytest.mark.asyncio
    async def test_operation_error_handling(self, mock_config, mock_router):
        """Test error handling in MCP operations."""
        # Mock operation failure
        mock_router.manager.call_tool.side_effect = Exception("MCP error")

        import agentic_core.L4_state.caching.redis_mcp_client as client_module
        original_config = client_module.get_sovereign_config
        client_module.get_sovereign_config = lambda: mock_config

        try:
            client = SovereignRedisMCPClient()
            client.router = mock_router

            # Should return None on error instead of raising
            result = await client.get("test_key")
            assert result is None

            # Should return False on error for set/delete operations
            result = await client.set("test_key", "value")
            assert result is False

            result = await client.delete("test_key")
            assert result is False

            result = await client.keys("*")
            assert result == []
        finally:
            client_module.get_sovereign_config = original_config


if __name__ == "__main__":
    pytest.main([__file__])
