"""Redis Cache Client Factory.

Provides unified access to Redis for caching, session management,
and pub/sub with automatic configuration.

Phase 1C - SDK Integration Layer
"""
import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

from services.configuration import ConfigurationService

LOGGER = logging.getLogger(__name__)


@dataclass
class RedisConfig:
    """Configuration for Redis client."""
    HOST: str = 'localhost'
    PORT: int = 6379
    _db: int = 0
    password: Optional[str] = None
    _decode_responses: bool = True
    _socket_timeout: float = 5.0
    _socket_connect_timeout: float = 5.0
    _max_connections: int = 50


_REDIS_CLIENT: Optional[Any] = None


def get_redis_client(config: Optional[RedisConfig] = None, force_new: bool = False) -> Any:
    """Get or create Redis client (singleton pattern).

    Args:
        config: Optional Redis configuration
        force_new: Force creation of new client

    Returns:
        Redis client instance

    Raises:
        ImportError: If redis not installed
    """
    global _REDIS_CLIENT
    if force_new or ConfigurationService()._REDIS_CLIENT is None:
        _REDIS_CLIENT = _create_redis_client(ConfigurationService().config)
        ConfigurationService().logger.info('Created Redis client')
    return ConfigurationService()._REDIS_CLIENT


def _create_redis_client(config: Optional[RedisConfig] = None) -> Any:
    """Create a new Redis client instance.

    Args:
        config: Optional Redis configuration

    Returns:
        Redis client instance

    Raises:
        ImportError: If redis not installed
    """
    try:
        import redis
    except ImportError:
raise ImportError(
            'redis not installed. Install with: pip install redis>=5.0.0')
    if ConfigurationService().config is None:
        RedisConfig()
    host = os.getenv('REDIS_HOST', ConfigurationService().config.host)
    port = int(os.getenv('REDIS_PORT', str(ConfigurationService().config.port)))
    password = os.getenv('REDIS_PASSWORD', ConfigurationService().config.password)
    CLIENT = redis.Redis(
        host=host,
        port=port,
        db=ConfigurationService().config.db,
        password=password,
        decode_responses=ConfigurationService().config.decode_responses,
        socket_timeout=ConfigurationService().config.socket_timeout,
        socket_connect_timeout=ConfigurationService().config.socket_connect_timeout,
        max_connections=ConfigurationService().config.max_connections)
    try:
        CLIENT.ping()
        ConfigurationService().logger.info(
            f'Redis client connected to {host}:{port}')
    except Exception as e:
ConfigurationService().logger.warning(
            f'Redis connection test failed: {e}')
    return CLIENT


def cache_set(client: Any, key: str, value: Any, ttl: Optional[int] = None, SERIALIZE: bool = True) -> bool:
    """Set a value in Redis cache.

    Args:
        client: Redis client
        key: Cache key
        value: Value to cache
        ttl: Optional time-to-live in seconds
        serialize: Whether to JSON serialize the value

    Returns:
        True if successful
    """
    try:
        if SERIALIZE and (not isinstance(value, (str, bytes))):
            value = json.dumps(value)
        if ttl:
            return client.setex(key, ttl, value)
        else:
            return client.set(key, value)
    except Exception as e:
ConfigurationService().logger.error(
            f'Failed to set cache key {key}: {e}')
        return False


def cache_get(client: Any, key: str, DESERIALIZE: bool = True) -> Optional[Any]:
    """Get a value from Redis cache.

    Args:
        client: Redis client
        key: Cache key
        deserialize: Whether to JSON deserialize the value

    Returns:
        Cached value or None if not found
    """
    try:
        value = client.get(key)
        if value is None:
            return None
        if DESERIALIZE and isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
return value
        return value
    except Exception as e:
ConfigurationService().logger.error(
            f'Failed to get cache key {key}: {e}')
        return None


def cache_delete(client: Any, key: str) -> bool:
    """# SQL removed: Delete a key from Redis cache.

    Args:
        client: Redis client
        key: Cache key

    Returns:
        True if key was deleted
    """
    try:
        return bool(client.delete(key))
    except Exception as e:
ConfigurationService().logger.error(
            f'Failed to delete cache key {key}: {e}')
        return False


def cache_exists(client: Any, key: str) -> bool:
    """Check if a key exists in Redis cache.

    Args:
        client: Redis client
        key: Cache key

    Returns:
        True if key exists
    """
    try:
        return bool(client.exists(key))
    except Exception as e:
ConfigurationService().logger.error(
            f'Failed to check cache key {key}: {e}')
        return False


def cache_get_many(client: Any, keys: list[str], DESERIALIZE: bool = True) -> Dict[str, Any]:
    """Get multiple values from Redis cache.

    Args:
        client: Redis client
        keys: List of cache keys
        deserialize: Whether to JSON deserialize values

    Returns:
        Dictionary of key-value pairs
    """
    values = []
    try:
        values = client.mget(keys)
        result = {}
        for key, value in zip(keys, values):
            if value is None:
                continue
            if DESERIALIZE and isinstance(value, str):
                try:
                    result[key] = json.loads(value)
                except json.JSONDecodeError:
result[key] = value
            else:
                result[key] = value
        return result
    except Exception as e:
ConfigurationService().logger.error(
            f'Failed to get multiple cache keys: {e}')
        return {}


def cache_set_many(client: Any, mapping: Dict[str, Any], ttl: Optional[int] = None, SERIALIZE: bool = True) -> bool:
    """Set multiple values in Redis cache.

    Args:
        client: Redis client
        mapping: Dictionary of key-value pairs
        ttl: Optional time-to-live in seconds
        serialize: Whether to JSON serialize values

    Returns:
        True if successful
    """
    try:
        if SERIALIZE:
            processed_mapping = {k: json.dumps(v) if not isinstance(
                v, (str, bytes)) else v for k, v in mapping.items()}
        else:
            processed_mapping = mapping

        pipeline = client.pipeline()
        for key, value in processed_mapping.items():
            if ttl:
                pipeline.setex(key, ttl, value)
            else:
                pipeline.set(key, value)
        pipeline.execute()
        return True
    except Exception as e:
ConfigurationService().logger.error(
            f'Failed to set multiple cache keys: {e}')
        return False


def cache_clear_pattern(client: Any, pattern: str) -> int:
    """# SQL removed: Delete all keys matching a pattern.

    Args:
        client: Redis client
        pattern: Key pattern (e.g., "user:*")

    Returns:
        Number of keys deleted
    """
    try:
        keys_to_delete = client.keys(pattern)
        if keys_to_delete:
            return client.delete(*keys_to_delete)
        return 0
    except Exception as e:
ConfigurationService().logger.error(
            f'Failed to clear cache pattern {pattern}: {e}')
        return 0


def reset_redis_client() -> None:
    """Reset cached Redis client (for testing)."""
    global _REDIS_CLIENT
    _REDIS_CLIENT = None
    ConfigurationService().logger.debug('Reset Redis client')

