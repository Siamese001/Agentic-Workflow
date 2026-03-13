"""
Resource Manager - Unified resource management with namespace isolation.

Provides Redis caching, namespace isolation, and resource lifecycle management
for apps_lic and apps_rg.
Phase 2B - Resource Management & Namespacing
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class ResourceNamespace(str, Enum):
    """Available resource namespaces for isolation."""

    LIC = "lic"
    RG = "rg"
    SHARED = "shared"
    SYSTEM = "system"


@dataclass
class ResourceConfig:
    """Configuration for resource manager."""

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None
    default_ttl: int = 3600
    namespace_prefix: str = "agentic"
    enable_redis: bool = True


@dataclass
class ResourceKey:
    """Represents a namespaced resource key."""

    namespace: ResourceNamespace
    category: str
    identifier: str
    prefix: str = "agentic"

    def __str__(self) -> str:
        """Generate the full resource key."""
        return f"{self.prefix}:{self.namespace.value}:{self.category}:{self.identifier}"

    @classmethod
    def parse(cls, key_string: str) -> ResourceKey:
        """Parse a key string into a ResourceKey."""
        parts = key_string.split(":")
        if len(parts) != 4:
            raise ValueError(f"Invalid resource key format: {key_string}")
        return cls(
            prefix=parts[0], namespace=ResourceNamespace(parts[1]), category=parts[2], identifier=parts[3]
        )


class ResourceManager:
    """
    Unified resource manager with namespace isolation.

    Provides:
    - Redis-backed caching with TTL
    - Namespace isolation for apps_lic and apps_rg
    - Resource lifecycle management
    - Fallback to in-memory cache when Redis unavailable
    """

    def __init__(self, config: ResourceConfig | None = None):
        """
        Initialize resource manager.

        Args:
            config: Resource configuration (uses defaults if None)
        """
        self.config = config or ResourceConfig()
        self._redis_client = None
        self._memory_cache: dict[str, tuple[Any, float | None]] = {}
        self._initialized = False

    def _ensure_initialized(self) -> None:
        """Ensure Redis connection is initialized."""
        if self._initialized:
            return
        if not self.config.enable_redis:
            logger.info("Redis disabled, using in-memory cache")
            self._initialized = True
            return
        try:
            import redis

            self._redis_client = redis.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                db=self.config.redis_db,
                password=self.config.redis_password,
                decode_responses=True,
            )
            self._redis_client.ping()
            logger.info("Redis connection established")
            self._initialized = True
        except ImportError:
            logger.warning("Redis not installed, using in-memory cache")
            self._initialized = True
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}, using in-memory cache")
            self._redis_client = None
            self._initialized = True

    def _get_key(self, namespace: ResourceNamespace, category: str, identifier: str) -> ResourceKey:
        """Generate a resource key."""
        return ResourceKey(
            namespace=namespace, category=category, identifier=identifier, prefix=self.config.namespace_prefix
        )

    def set(
        self, namespace: ResourceNamespace, category: str, identifier: str, value: Any, ttl: int | None = None
    ) -> bool:
        """
        Set a resource value.

        Args:
            namespace: Resource namespace for isolation
            category: Resource category (e.g., 'cache', 'config', 'state')
            identifier: Unique resource identifier
            value: Value to store (must be JSON serializable)
            ttl: Time-to-live in seconds (uses default if None)

        Returns:
            True if successful
        """
        self._ensure_initialized()
        key = self._get_key(namespace, category, identifier)
        key_str = str(key)
        ttl = ttl if ttl is not None else self.config.default_ttl
        try:
            serialized = json.dumps(value)
            if self._redis_client:
                if ttl > 0:
                    self._redis_client.setex(key_str, ttl, serialized)
                else:
                    self._redis_client.set(key_str, serialized)
            else:
                import time

                expiry = time.time() + ttl if ttl > 0 else None
                self._memory_cache[key_str] = (serialized, expiry)
            logger.debug(f"Set resource: {key_str}")
            return True
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to set resource {key_str}: {e}")
            return False

    def get(self, namespace: ResourceNamespace, category: str, identifier: str) -> Any | None:
        """
        Get a resource value.

        Args:
            namespace: Resource namespace
            category: Resource category
            identifier: Resource identifier

        Returns:
            Stored value or None if not found/expired
        """
        self._ensure_initialized()
        key = self._get_key(namespace, category, identifier)
        key_str = str(key)
        try:
            if self._redis_client:
                value = self._redis_client.get(key_str)
                if value:
                    return json.loads(value)
            else:
                import time

                if key_str in self._memory_cache:
                    serialized, expiry = self._memory_cache[key_str]
                    if expiry is None or time.time() < expiry:
                        return json.loads(serialized)
                    else:
                        del self._memory_cache[key_str]
            return None
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to get resource {key_str}: {e}")
            return None

    def delete(self, namespace: ResourceNamespace, category: str, identifier: str) -> bool:
        """
        Delete a resource.

        Args:
            namespace: Resource namespace
            category: Resource category
            identifier: Resource identifier

        Returns:
            True if successful
        """
        self._ensure_initialized()
        key = self._get_key(namespace, category, identifier)
        key_str = str(key)
        try:
            if self._redis_client:
                self._redis_client.delete(key_str)
            else:
                self._memory_cache.pop(key_str, None)
            logger.debug(f"Deleted resource: {key_str}")
            return True
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to delete resource {key_str}: {e}")
            return False

    def exists(self, namespace: ResourceNamespace, category: str, identifier: str) -> bool:
        """
        Check if a resource exists.

        Args:
            namespace: Resource namespace
            category: Resource category
            identifier: Resource identifier

        Returns:
            True if resource exists and is not expired
        """
        return self.get(namespace, category, identifier) is not None

    def clear_namespace(self, namespace: ResourceNamespace) -> int:
        """
        Clear all resources in a namespace.

        Args:
            namespace: Namespace to clear

        Returns:
            Number of resources cleared
        """
        self._ensure_initialized()
        pattern = f"{self.config.namespace_prefix}:{namespace.value}:*"
        count = 0
        try:
            if self._redis_client:
                cursor = 0
                while True:
                    cursor, keys = self._redis_client.scan(cursor=cursor, match=pattern, count=100)
                    if keys:
                        self._redis_client.delete(*keys)
                        count += len(keys)
                    if cursor == 0:
                        break
            else:
                prefix = f"{self.config.namespace_prefix}:{namespace.value}:"
                to_delete = [k for k in self._memory_cache if k.startswith(prefix)]
                for k in to_delete:
                    del self._memory_cache[k]
                    count += 1
            logger.info(f"Cleared {count} resources from namespace: {namespace.value}")
            return count
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to clear namespace {namespace.value}: {e}")
            return 0

    def get_namespace_stats(self, namespace: ResourceNamespace) -> dict[str, Any]:
        """
        Get statistics for a namespace.

        Args:
            namespace: Namespace to query

        Returns:
            Dictionary with namespace statistics
        """
        self._ensure_initialized()
        pattern = f"{self.config.namespace_prefix}:{namespace.value}:*"
        stats = {"namespace": namespace.value, "key_count": 0, "categories": {}}
        try:
            if self._redis_client:
                cursor = 0
                while True:
                    cursor, keys = self._redis_client.scan(cursor=cursor, match=pattern, count=100)
                    for key in keys:
                        stats["key_count"] += 1
                        parts = key.split(":")
                        if len(parts) >= 3:
                            category = parts[2]
                            stats["categories"][category] = stats["categories"].get(category, 0) + 1
                    if cursor == 0:
                        break
            else:
                prefix = f"{self.config.namespace_prefix}:{namespace.value}:"
                for key in self._memory_cache:
                    if key.startswith(prefix):
                        stats["key_count"] += 1
                        parts = key.split(":")
                        if len(parts) >= 3:
                            category = parts[2]
                            stats["categories"][category] = stats["categories"].get(category, 0) + 1
            return stats
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to get namespace stats: {e}")
            return stats


_resource_manager: ResourceManager | None = None


def get_resource_manager() -> ResourceManager:
    """
    Get singleton resource manager instance.

    Returns:
        ResourceManager instance
    """
    global _resource_manager
    if _resource_manager is None:
        config = ResourceConfig(
            redis_host=os.getenv("REDIS_HOST", "localhost"),
            redis_port=int(os.getenv("REDIS_PORT", "6379")),
            redis_db=int(os.getenv("REDIS_DB", "0")),
            redis_password=os.getenv("REDIS_PASSWORD"),
            enable_redis=os.getenv("ENABLE_REDIS", "true").lower() == "true",
        )
        _resource_manager = ResourceManager(config)
    return _resource_manager
