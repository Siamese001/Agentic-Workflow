"""
Redis client provider for caching operations.

Isolates Redis SDK dependencies to the providers layer
and provides a clean interface for cache operations.
"""

from __future__ import annotations

from typing import Optional

try:
    import redis  # type: ignore
except ImportError as exc:
    raise ImportError("redis package not installed. Install with: pip install redis") from exc


class RedisClient:
    """Provider client for Redis operations."""
    
    def __init__(self, host: str = "localhost", port: int = 6379, 
                 db: int = 0, password: Optional[str] = None,
                 decode_responses: bool = True, **kwargs):
        """Initialize Redis client with connection parameters."""
        self.client = redis.Redis(
            host=host, port=port, db=db, password=password,
            decode_responses=decode_responses, **kwargs
        )
    
    def get(self, key: str) -> Optional[str]:
        """Get value from Redis."""
        return self.client.get(key)
    
    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """Set value in Redis with optional expiration."""
        return self.client.set(key, value, ex=ex)
    
    def delete(self, key: str) -> int:
        """Delete key from Redis."""
        return self.client.delete(key)
    
    def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        return self.client.exists(key)
    
    def ping(self) -> bool:
        """Ping Redis server to check connectivity."""
        return self.client.ping()
    
    def close(self) -> None:
        """Close Redis connection."""
        self.client.close()


def init_redis_client(url: Optional[str] = None, *, timeout_s: float = 1.0) -> RedisClient:
    """Initialize a Redis client from URL or default parameters."""
    if url:
        # Parse redis URL: redis://[:password@]host:port/db
        import urllib.parse
        parsed = urllib.parse.urlparse(url)
        return RedisClient(
            host=parsed.hostname or "localhost",
            port=parsed.port or 6379,
            db=int(parsed.path.lstrip('/')) if parsed.path else 0,
            password=parsed.password,
            socket_timeout=timeout_s
        )
    else:
        return RedisClient(socket_timeout=timeout_s)
