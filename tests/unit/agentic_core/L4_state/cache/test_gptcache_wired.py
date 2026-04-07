"""Unit tests for NativePersistentCacheClient integration in SemanticCacheManager"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[5]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agentic_core.L4_state.utils.memory.semantic_cache_manager import SemanticCacheManager


def test_semantic_cache_manager_imports_gptcache() -> None:
    """Test that SemanticCacheManager can import NativePersistentCacheClient (via GPTCacheClient alias)."""
    try:
        from agentic_core.L4_state.cache.gptcache_client import GPTCacheClient
        assert GPTCacheClient is not None
    except ImportError:
        pytest.skip("ChromaDB not installed")


def test_semantic_cache_manager_initializes_gptcache() -> None:
    """Test that SemanticCacheManager initializes NativePersistentCacheClient in _initialize."""
    # Reset singleton
    SemanticCacheManager._instance = None
    
    with patch('agentic_core.L4_state.utils.memory.semantic_cache_manager.GPTCacheClient') as mock_gptcache:
        mock_instance = MagicMock()
        mock_instance._cache = "real"  # Not mock mode
        mock_gptcache.return_value = mock_instance
        
        cache = SemanticCacheManager.get_instance()
        
        # Verify GPTCacheClient was instantiated
        mock_gptcache.assert_called_once()
        
        # Verify gptcache_enabled is True
        assert cache.gptcache_enabled is True
        assert cache._gptcache is not None


def test_semantic_cache_manager_gptcache_mock_fallback() -> None:
    """Test that SemanticCacheManager degrades gracefully when NativePersistentCacheClient is in mock mode."""
    # Reset singleton
    SemanticCacheManager._instance = None
    
    with patch('agentic_core.L4_state.utils.memory.semantic_cache_manager.GPTCacheClient') as mock_gptcache:
        mock_instance = MagicMock()
        mock_instance._cache = "mock"  # Mock mode
        mock_gptcache.return_value = mock_instance
        
        cache = SemanticCacheManager.get_instance()
        
        # Verify gptcache_enabled is False when in mock mode
        assert cache.gptcache_enabled is False


def test_semantic_cache_manager_gptcache_import_failure() -> None:
    """Test that SemanticCacheManager degrades gracefully when NativePersistentCacheClient import fails."""
    # Reset singleton
    SemanticCacheManager._instance = None
    
    with patch('agentic_core.L4_state.utils.memory.semantic_cache_manager.GPTCacheClient', side_effect=ImportError):
        cache = SemanticCacheManager.get_instance()
        
        # Verify gptcache_enabled is False on import failure
        assert cache.gptcache_enabled is False


def test_semantic_cache_manager_recall_uses_gptcache() -> None:
    """Test that recall method uses NativePersistentCacheClient when enabled."""
    # Reset singleton
    SemanticCacheManager._instance = None
    
    with patch('agentic_core.L4_state.utils.memory.semantic_cache_manager.GPTCacheClient') as mock_gptcache:
        mock_instance = MagicMock()
        mock_instance._cache = "real"
        # Return JSON string with _metadata namespace to match implementation
        mock_instance.get.return_value = '{"result": "cached", "_metadata": {"namespace": "test_namespace"}}'
        mock_gptcache.return_value = mock_instance
        
        cache = SemanticCacheManager.get_instance()
        
        # Disable Redis to force L2 cache usage
        cache.redis_enabled = False
        
        # Call recall
        result = cache.recall("test context", "test_namespace")
        
        # Verify GPTCache.get was called
        mock_instance.get.assert_called_once()
        # Verify result was returned (namespace match)
        assert result is not None
        assert result["result"] == "cached"


def test_semantic_cache_manager_promote_uses_gptcache() -> None:
    """Test that promote_to_long_term uses NativePersistentCacheClient when enabled."""
    import asyncio
    
    # Reset singleton
    SemanticCacheManager._instance = None
    
    with patch('agentic_core.L4_state.utils.memory.semantic_cache_manager.GPTCacheClient') as mock_gptcache:
        mock_instance = MagicMock()
        mock_instance._cache = "real"
        mock_gptcache.return_value = mock_instance
        
        cache = SemanticCacheManager.get_instance()
        
        # Call promote_to_long_term
        result = asyncio.run(cache.promote_to_long_term(
            "test context",
            "test_namespace",
            {"result": "test"},
            0.9  # Above default threshold
        ))
        
        # Verify GPTCache.set was called
        mock_instance.set.assert_called_once()


def test_semantic_cache_manager_stats_include_gptcache_hits() -> None:
    """Test that get_statistics includes gptcache_hits (L2 cache hits)."""
    # Reset singleton
    SemanticCacheManager._instance = None
    
    with patch('agentic_core.L4_state.utils.memory.semantic_cache_manager.GPTCacheClient') as mock_gptcache:
        mock_instance = MagicMock()
        mock_instance._cache = "real"
        mock_gptcache.return_value = mock_instance
        
        cache = SemanticCacheManager.get_instance()
        
        # Increment gptcache_hits
        with cache._lock:
            cache.stats["gptcache_hits"] = 5
        
        stats = cache.get_statistics()
        
        # Verify gptcache_hits is in stats
        assert "gptcache_hits" in stats
        assert stats["gptcache_hits"] == 5
        assert stats["total_hits"] == 5 + stats["redis_hits"]


def test_native_persistent_cache_close_called() -> None:
    """Test that close() method is called on NativePersistentCacheClient to prevent resource leaks."""
    try:
        from agentic_core.L4_state.cache.gptcache_client import NativePersistentCacheClient
    except ImportError:
        pytest.skip("ChromaDB not installed")
    
    # Create cache instance
    cache = NativePersistentCacheClient(cache_dir="artifacts/test_gptcache_close")
    
    # Verify it's in real mode
    if cache._cache == "mock":
        pytest.skip("ChromaDB not available, using mock mode")
    
    # Call close
    cache.close()
    
    # Verify close was successful (no exception raised)
    assert True
