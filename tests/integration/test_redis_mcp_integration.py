"""
Integration tests for Redis MCP client functionality.
Tests the sovereign Redis MCP client with real Redis operations.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import importlib
import os

def _set_redis_mcp_enabled(monkeypatch, enabled: bool):
    """Helper to toggle REDIS_MCP_ENABLED env and reload dependent modules."""
    if enabled:
        monkeypatch.setenv("REDIS_MCP_ENABLED", "true")
    else:
        monkeypatch.delenv("REDIS_MCP_ENABLED", raising=False)
    
    # reload sovereign_config first
    import agentic_core.config.core.sovereign_config as sc
    importlib.reload(sc)
    
    # reload redis_mcp_client which imports/reads sovereign_config
    import agentic_core.L4_state.caching.redis_mcp_client as rmc
    importlib.reload(rmc)
    
    return sc, rmc


class TestRedisMCPIntegration:
    """Test Redis MCP client integration."""

    def test_get_redis_client_singleton(self, monkeypatch):
        """Test that get_redis_client returns singleton instance."""
        # Enable Redis MCP for this test
        sc, rmc = _set_redis_mcp_enabled(monkeypatch, True)
        
        # Reset singleton
        rmc._redis_client = None
        
        client1 = rmc.get_redis_client()
        client2 = rmc.get_redis_client()
        
        assert client1 is client2

    def test_client_init_disabled(self, monkeypatch):
        """Test client initialization fails when Redis MCP disabled."""
        sc, rmc = _set_redis_mcp_enabled(monkeypatch, False)
        
        with pytest.raises(ValueError, match="Redis MCP disabled"):
            rmc.SovereignRedisMCPClient()

    def test_client_init_no_redis_package(self, monkeypatch):
        """Test client initialization fails when redis package not available."""
        sc, rmc = _set_redis_mcp_enabled(monkeypatch, True)
        
        with patch.dict('sys.modules', {'redis': None}):
            with patch('builtins.__import__', side_effect=ImportError("No module named 'redis'")):
                with pytest.raises(RuntimeError, match="Redis package required"):
                    rmc.SovereignRedisMCPClient()

    @pytest.mark.asyncio
    async def test_redis_get_operation(self, monkeypatch):
        """Test Redis GET operation."""
        sc, rmc = _set_redis_mcp_enabled(monkeypatch, True)
        
        # Mock config defaults
        with patch.object(sc.SovereignConfigManager, 'redis_cache_prefix', 'test:'), \
             patch.object(sc.SovereignConfigManager, 'redis_max_key_length', 250), \
             patch('redis.from_url') as mock_redis_from_url:
            mock_redis_client = MagicMock()
            mock_redis_client.get.return_value = b"test_value"
            mock_redis_from_url.return_value = mock_redis_client
            
            client = rmc.SovereignRedisMCPClient()
            result = await client.get("test_key")
            
            assert result == "test_value"
            mock_redis_client.get.assert_called_once_with("test:test_key")

    @pytest.mark.asyncio
    async def test_redis_set_operation(self, monkeypatch):
        """Test Redis SET operation."""
        sc, rmc = _set_redis_mcp_enabled(monkeypatch, True)
        
        # Mock config defaults
        with patch.object(sc.SovereignConfigManager, 'redis_cache_prefix', 'test:'), \
             patch.object(sc.SovereignConfigManager, 'redis_max_key_length', 250), \
             patch.object(sc.SovereignConfigManager, 'redis_default_ttl_seconds', 3600), \
             patch('redis.from_url') as mock_redis_from_url:
            mock_redis_client = MagicMock()
            mock_redis_client.setex.return_value = True
            mock_redis_from_url.return_value = mock_redis_client
            
            client = rmc.SovereignRedisMCPClient()
            result = await client.set("test_key", "test_value", ttl=300)
            
            assert result is True
            mock_redis_client.setex.assert_called_once_with("test:test_key", 300, "test_value")

    @pytest.mark.asyncio
    async def test_redis_delete_operation(self, monkeypatch):
        """Test Redis DELETE operation."""
        sc, rmc = _set_redis_mcp_enabled(monkeypatch, True)
        
        # Mock config defaults
        with patch.object(sc.SovereignConfigManager, 'redis_cache_prefix', 'test:'), \
             patch.object(sc.SovereignConfigManager, 'redis_max_key_length', 250), \
             patch('redis.from_url') as mock_redis_from_url:
            mock_redis_client = MagicMock()
            mock_redis_client.delete.return_value = 1
            mock_redis_from_url.return_value = mock_redis_client
            
            client = rmc.SovereignRedisMCPClient()
            result = await client.delete("test_key")
            
            assert result is True
            mock_redis_client.delete.assert_called_once_with("test:test_key")

    @pytest.mark.asyncio
    async def test_redis_keys_operation(self, monkeypatch):
        """Test Redis KEYS operation."""
        sc, rmc = _set_redis_mcp_enabled(monkeypatch, True)
        
        # Mock config defaults
        with patch.object(sc.SovereignConfigManager, 'redis_cache_prefix', 'test:'), \
             patch.object(sc.SovereignConfigManager, 'redis_max_key_length', 250), \
             patch('redis.from_url') as mock_redis_from_url:
            mock_redis_client = MagicMock()
            mock_redis_client.keys.return_value = [b"test:key1", b"test:key2"]
            mock_redis_from_url.return_value = mock_redis_client
            
            client = rmc.SovereignRedisMCPClient()
            result = await client.keys("*")
            
            assert result == ["key1", "key2"]
            mock_redis_client.keys.assert_called_once_with("test:*")

    @pytest.mark.asyncio
    async def test_key_length_validation(self, monkeypatch):
        """Test key length validation."""
        sc, rmc = _set_redis_mcp_enabled(monkeypatch, True)
        
        # Mock config with small max length
        with patch.object(sc.SovereignConfigManager, 'redis_max_key_length', 10), \
             patch('redis.from_url') as mock_redis_from_url:
            mock_redis_from_url.return_value = MagicMock()
            
            client = rmc.SovereignRedisMCPClient()
            
            with pytest.raises(ValueError, match="Key exceeds sovereign limit"):
                await client.get("this_key_is_too_long")

    @pytest.mark.asyncio
    async def test_operation_error_handling(self, monkeypatch):
        """Test error handling in Redis operations."""
        sc, rmc = _set_redis_mcp_enabled(monkeypatch, True)
        
        with patch('redis.from_url') as mock_redis_from_url:
            mock_redis_client = MagicMock()
            mock_redis_client.get.side_effect = Exception("Redis error")
            mock_redis_from_url.return_value = mock_redis_client
            
            client = rmc.SovereignRedisMCPClient()
            
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
