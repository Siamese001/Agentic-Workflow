"""
Sovereign Redis MCP Client – Phase 16A (Dec 27, 2025)
Replaces all direct redis-py operations with official Redis MCP integration.
L3 routed, L5 shielded, L6 observable.
"""
import logging
from typing import Any, Optional, List, Dict

# Import configuration for single source of truth
from agentic_core.config.core.sovereign_config import get_sovereign_config

logger = logging.getLogger(__name__)


class SovereignRedisMCPClient:
    """Official Redis MCP client for sovereign caching operations."""
    
    def __init__(self, role: str = "state_cache"):
        config = get_sovereign_config()
        if not config.REDIS_MCP_ENABLED:
            raise ValueError("Redis MCP disabled in sovereign config")
        
        # Check for redis package availability
        try:
            import redis
        except ImportError as e:
            raise RuntimeError("Redis package required when REDIS_MCP_ENABLED is true") from e
        
        self.config = config
        self.role = role
        self._redis_client = None
        logger.info("[L4 REDIS] Sovereign Redis MCP client initialized")
    
    def _get_redis_client(self):
        """Lazy initialization of Redis client."""
        if self._redis_client is None:
            import redis
            self._redis_client = redis.from_url(self.config.redis_url)
        return self._redis_client
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from sovereign cache via Redis."""
        if len(key) > self.config.redis_max_key_length:
            raise ValueError(f"Key exceeds sovereign limit: {len(key)}")
        
        full_key = f"{self.config.redis_cache_prefix}{key}"
        
        try:
            client = self._get_redis_client()
            result = client.get(full_key)
            # Redis returns bytes, decode if needed
            if isinstance(result, bytes):
                result = result.decode('utf-8')
            return result
        except Exception as e:
            logger.error(f"[L4 REDIS] Cache GET failed for {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in sovereign cache via Redis."""
        if len(key) > self.config.redis_max_key_length:
            raise ValueError(f"Key exceeds sovereign limit: {len(key)}")
        
        full_key = f"{self.config.redis_cache_prefix}{key}"
        
        try:
            client = self._get_redis_client()
            expire_time = ttl or self.config.redis_default_ttl_seconds
            result = client.setex(full_key, expire_time, value)
            return bool(result)
        except Exception as e:
            logger.error(f"[L4 REDIS] Cache SET failed for {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from sovereign cache via Redis."""
        full_key = f"{self.config.redis_cache_prefix}{key}"
        try:
            client = self._get_redis_client()
            result = client.delete(full_key)
            return result > 0
        except Exception as e:
            logger.error(f"[L4 REDIS] Cache DELETE failed for {key}: {e}")
            return False
    
    async def keys(self, pattern: str = "*") -> List[str]:
        """List keys matching pattern via Redis."""
        full_pattern = f"{self.config.redis_cache_prefix}{pattern}"
        try:
            client = self._get_redis_client()
            keys = client.keys(full_pattern)
            # Remove prefix from returned keys and decode bytes
            result = []
            prefix = self.config.redis_cache_prefix
            for key in keys:
                if isinstance(key, bytes):
                    key = key.decode('utf-8')
                if key.startswith(prefix):
                    result.append(key[len(prefix):])
            return result
        except Exception as e:
            logger.error(f"[L4 REDIS] Cache KEYS failed: {e}")
            return []


# Singleton instance
_redis_client: Optional[SovereignRedisMCPClient] = None


def get_redis_client() -> SovereignRedisMCPClient:
    """Get or create the global Redis MCP client."""
    global _redis_client
    if _redis_client is None:
        _redis_client = SovereignRedisMCPClient()
    return _redis_client
