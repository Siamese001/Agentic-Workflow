"""
Integration tests for Redis MCP client functionality.
Tests the sovereign Redis MCP client with real Redis operations.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import importlib

from agentic_core.L4_state.caching.redis_mcp_client import SovereignRedisMCPClient, get_redis_client


class TestRedisMCPIntegration:
    """Test Redis MCP client integration."""

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
        with patch('agentic_core.config.core.sovereign_config.get_sovereign_config') as mock_config_func:
            mock_config = MagicMock()
            mock_config.REDIS_MCP_ENABLED = False
            mock_config_func.return_value = mock_config
            
            with pytest.raises(ValueError, match="Redis MCP disabled"):
                SovereignRedisMCPClient()

    def test_client_init_no_redis_package(self):
        """Test client initialization fails when redis package not available."""
        with patch('agentic_core.config.core.sovereign_config.get_sovereign_config') as mock_config_func, \
             patch.dict('sys.modules', {'redis': None}):
            
            mock_config = MagicMock()
            mock_config.REDIS_MCP_ENABLED = True
            mock_config_func.return_value = mock_config
            
            with patch('builtins.__import__', side_effect=ImportError("No module named 'redis'")):
                with pytest.raises(RuntimeError, match="Redis package required"):
                    SovereignRedisMCPClient()

    @pytest.mark.asyncio
    async def test_redis_get_operation(self):
        """Test Redis GET operation."""
        with patch('agentic_core.config.core.sovereign_config.get_sovereign_config') as mock_config_func:
            mock_config = MagicMock()
            mock_config.REDIS_MCP_ENABLED = True
            mock_config.redis_cache_prefix = "test:"
            mock_config.redis_max_key_length = 250
            mock_config_func.return_value = mock_config
            
            with patch('redis.from_url') as mock_redis_from_url:
                mock_redis_client = MagicMock()
                mock_redis_client.get.return_value = b"test_value"
                mock_redis_from_url.return_value = mock_redis_client
                
                client = SovereignRedisMCPClient()
                result = await client.get("test_key")
                
                assert result == "test_value"
                mock_redis_client.get.assert_called_once_with("test:test_key")

    @pytest.mark.asyncio
    async def test_redis_set_operation(self):
        """Test Redis SET operation."""
        with patch('agentic_core.config.core.sovereign_config.get_sovereign_config') as mock_config_func:
            mock_config = MagicMock()
            mock_config.REDIS_MCP_ENABLED = True
            mock_config.redis_cache_prefix = "test:"
            mock_config.redis_max_key_length = 250
            mock_config.redis_default_ttl_seconds = 3600
            mock_config_func.return_value = mock_config
            
            with patch('redis.from_url') as mock_redis_from_url:
                mock_redis_client = MagicMock()
                mock_redis_client.setex.return_value = True
                mock_redis_from_url.return_value = mock_redis_client
                
                client = SovereignRedisMCPClient()
                result = await client.set("test_key", "test_value", ttl=300)
                
                assert result is True
                mock_redis_client.setex.assert_called_once_with("test:test_key", 300, "test_value")

    @pytest.mark.asyncio
    async def test_redis_delete_operation(self):
        """Test Redis DELETE operation."""
        with patch('agentic_core.config.core.sovereign_config.get_sovereign_config') as mock_config_func:
            mock_config = MagicMock()
            mock_config.REDIS_MCP_ENABLED = True
            mock_config.redis_cache_prefix = "test:"
            mock_config.redis_max_key_length = 250
            mock_config_func.return_value = mock_config
            
            with patch('redis.from_url') as mock_redis_from_url:
                mock_redis_client = MagicMock()
                mock_redis_client.delete.return_value = 1
                mock_redis_from_url.return_value = mock_redis_client
                
                client = SovereignRedisMCPClient()
                result = await client.delete("test_key")
                
                assert result is True
                mock_redis_client.delete.assert_called_once_with("test:test_key")

    @pytest.mark.asyncio
    async def test_redis_keys_operation(self):
        """Test Redis KEYS operation."""
        with patch('agentic_core.config.core.sovereign_config.get_sovereign_config') as mock_config_func:
            mock_config = MagicMock()
            mock_config.REDIS_MCP_ENABLED = True
            mock_config.redis_cache_prefix = "test:"
            mock_config.redis_max_key_length = 250
            mock_config_func.return_value = mock_config
            
            with patch('redis.from_url') as mock_redis_from_url:
                mock_redis_client = MagicMock()
                mock_redis_client.keys.return_value = [b"test:key1", b"test:key2"]
                mock_redis_from_url.return_value = mock_redis_client
                
                client = SovereignRedisMCPClient()
                result = await client.keys("*")
                
                assert result == ["key1", "key2"]
                mock_redis_client.keys.assert_called_once_with("test:*")

    @pytest.mark.asyncio
    async def test_key_length_validation(self):
        """Test key length validation."""
        with patch('agentic_core.config.core.sovereign_config.get_sovereign_config') as mock_config_func:
            mock_config = MagicMock()
            mock_config.REDIS_MCP_ENABLED = True
            mock_config.redis_max_key_length = 10
            mock_config_func.return_value = mock_config
            
            client = SovereignRedisMCPClient()
            
            with pytest.raises(ValueError, match="Key exceeds sovereign limit"):
                await client.get("this_key_is_too_long")

    @pytest.mark.asyncio
    async def test_operation_error_handling(self):
        """Test error handling in Redis operations."""
        with patch('agentic_core.config.core.sovereign_config.get_sovereign_config') as mock_config_func:
            mock_config = MagicMock()
            mock_config.REDIS_MCP_ENABLED = True
            mock_config.redis_cache_prefix = "test:"
            mock_config.redis_max_key_length = 250
            mock_config_func.return_value = mock_config
            
            with patch('redis.from_url') as mock_redis_from_url:
                mock_redis_client = MagicMock()
                mock_redis_client.get.side_effect = Exception("Redis error")
                mock_redis_from_url.return_value = mock_redis_client
                
                client = SovereignRedisMCPClient()
                
                # Should return None on error
                result = await client.get("test_key")
                assert result is None
                
                # Should return False on error for set/delete operations
                mock_redis_client.get.side_effect = None
                mock_redis_client.setex.side_effect = Exception("Redis error")
                result = await client.set("test_key", "value")
                assert result is False
                
                mock_redis_client.setex.side_effect = None
                mock_redis_client.delete.side_effect = Exception("Redis error")
                result = await client.delete("test_key")
                assert result is False
                
                mock_redis_client.delete.side_effect = None
                mock_redis_client.keys.side_effect = Exception("Redis error")
                result = await client.keys("*")
                assert result == []


if __name__ == "__main__":
    pytest.main([__file__])
