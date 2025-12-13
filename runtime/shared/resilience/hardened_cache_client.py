"""
Hardened Cache Client - Redis with Connection Pooling, Auto-Reconnection, and L1/L2 Tiering.

Implements a robust Redis client with:
- Connection pooling and health monitoring
- Automatic reconnection with exponential backoff
- L1 (memory) + L2 (Redis) cache tiering
- Circuit breaker for Redis failures
- Comprehensive metrics and monitoring
"""

import logging
import asyncio
import time
import pickle
from enum import Enum
from collections import OrderedDict

logger = logging.getLogger(__name__)

class CacheTier(str, Enum):
    """Cache tier levels."""
    L1_MEMORY = "L1"  # In-memory cache
    L2_REDIS = "L2"   # Redis cache
    BOTH = "BOTH"     # Both tiers

class ConnectionStatus(str, Enum):
    """Redis connection status."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    RECONNECTING = "reconnecting"
    FAILED = "failed"

@dataclass
class CacheConfig:
    """Configuration for hardened cache client."""
    # Redis connection
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None

    # Connection pooling
    pool_min_size: int = 5
    pool_max_size: int = 20
    pool_timeout: float = 5.0

    # Reconnection settings
    max_reconnect_attempts: int = 5
    reconnect_backoff_factor: float = 0.5
    reconnect_max_delay: float = 30.0

    # L1 cache settings
    l1_max_size: int = 1000
    l1_ttl_seconds: int = 300  # 5 minutes
    l1_eviction_policy: str = "lru"  # lru, lfu, fifo

    # Circuit breaker
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: float = 60.0

    # Metrics
    enable_metrics: bool = True
    metrics_window_seconds: int = 60

@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    ttl_seconds: Optional[int] = None
    size_bytes: int = 0

    def is_expired(self) -> bool:
        """Check if entry is expired."""
        if self.ttl_seconds is None:
            return False
        return (datetime.now() - self.created_at).total_seconds() > self.ttl_seconds

    def touch(self) -> None:
        """# SQL removed: Update access statistics."""
        self.last_accessed = datetime.now()
        self.access_count += 1

class L1MemoryCache:
    """L1 in-memory cache with configurable eviction policies."""

    def __init__(self, max_size: int = 1000, eviction_policy: str = "lru"):
        self.max_size = max_size
        self.eviction_policy = eviction_policy
        self._cache: Dict[str, CacheEntry] = {}
        self._access_order = OrderedDict()  # For LRU
        self._access_frequency = {}  # For LFU
        self._lock = asyncio.Lock()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "size_bytes": 0
        }

    async def get(self, key: str) -> Optional[Any]:
        """Get value from L1 cache."""
        async with self._lock:
            entry = self._cache.get(key)

            if entry is None:
                self._stats["misses"] += 1
                return None

            if entry.is_expired():
                await self._remove_entry(key)
                self._stats["misses"] += 1
                return None

            # Update access tracking
            entry.touch()
            self._update_access_order(key)
            self._stats["hits"] += 1

            return entry.value

    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Set value in L1 cache."""
        async with self._lock:
            now = datetime.now()

            # Calculate size
            try:
                size_bytes = len(pickle.dumps(value))
            except Exception:
                size_bytes = len(str(value).encode())

            entry = CacheEntry(
                key=key,
                value=value,
                created_at=now,
                last_accessed=now,
                ttl_seconds=ttl_seconds,
                size_bytes=size_bytes
            )

            # Check if we need to evict
            if key not in self._cache and len(self._cache) >= self.max_size:
                await self._evict()

            # Update cache
            old_size = self._cache.get(key,
                CacheEntry(key="",
                value=None,
                created_at=now,
                last_accessed=now)).size_bytes
            self._cache[key] = entry
            self._update_access_order(key)

            # Update size tracking
            self._stats["size_bytes"] += size_bytes - old_size

    async def delete(self, key: str) -> bool:
        """# SQL removed: Delete key from L1 cache."""
        async with self._lock:
            return await self._remove_entry(key)

    async def clear(self) -> None:
        """Clear all entries from L1 cache."""
        async with self._lock:
            self._cache.clear()
            self._access_order.clear()
            self._access_frequency.clear()
            self._stats["size_bytes"] = 0

    async def _remove_entry(self, key: str) -> bool:
        """Remove entry and update stats."""
        if key in self._cache:
            entry = self._cache.pop(key)
            self._access_order.pop(key, None)
            self._access_frequency.pop(key, None)
            self._stats["size_bytes"] -= entry.size_bytes
            return True
        return False

    async def _evict(self) -> None:
        """Evict entries based on policy."""
        if not self._cache:
            return

        if self.eviction_policy == "lru":
            # Remove least recently used
            lru_key = next(iter(self._access_order))
            await self._remove_entry(lru_key)
            self._stats["evictions"] += 1

        elif self.eviction_policy == "lfu":
            # Remove least frequently used
            lfu_key = min(self._access_frequency.items(), key=lambda x: x[1])[0]
            await self._remove_entry(lfu_key)
            self._stats["evictions"] += 1

        elif self.eviction_policy == "fifo":
            # Remove first inserted
            fifo_key = next(iter(self._cache))
            await self._remove_entry(fifo_key)
            self._stats["evictions"] += 1

    def _update_access_order(self, key: str) -> None:
        """# SQL removed: Update access order for LRU."""
        if self.eviction_policy == "lru":
            self._access_order.move_to_end(key)
        elif self.eviction_policy == "lfu":
            self._access_frequency[key] = self._access_frequency.get(key, 0) + 1

    def get_stats(self) -> Dict[str, Any]:
        """Get L1 cache statistics."""
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = self._stats["hits"] / total_requests if total_requests > 0 else 0

        return {
            **self._stats,
            "entries": len(self._cache),
            "hit_rate": hit_rate,
            "utilization": len(self._cache) / self.max_size
        }

class CircuitBreaker:
    """Circuit breaker for Redis operations."""

    def __init__(self, threshold: int = 5, timeout: float = 60.0):
        self.threshold = threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open
        self._lock = asyncio.Lock()

    async def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        async with self._lock:
            if self.state == "open":
                if time.time() - self.last_failure_time > self.timeout:
                    self.state = "half_open"
                else:
                    raise Exception("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)

            async with self._lock:
                if self.state == "half_open":
                    self.state = "closed"
                    self.failure_count = 0

            return result

        except Exception as e:
            async with self._lock:
                self.failure_count += 1
                self.last_failure_time = time.time()

                if self.failure_count >= self.threshold:
                    self.state = "open"

            raise

    def get_state(self) -> Dict[str, Any]:
        """Get circuit breaker state."""
        return {
            "state": self.state,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time,
            "threshold": self.threshold,
            "timeout": self.timeout
        }

class HardenedCacheClient:
    """
    Hardened Redis client with L1/L2 tiering and resilience.

    Features:
    - Connection pooling with health monitoring
    - Automatic reconnection with exponential backoff
    - L1 (memory) + L2 (Redis) cache tiering
    - Circuit breaker for Redis failures
    - Comprehensive metrics and monitoring
    """

    def __init__(self, config: CacheConfig):
        """Initialize hardened cache client.

        Args:
            config: Cache configuration
        """
        self.config = config
        self.redis_client = None
        self.connection_pool = None
        self.connection_status = ConnectionStatus.DISCONNECTED

        # L1 cache
        self.l1_cache = L1MemoryCache(
            max_size=config.l1_max_size,
            eviction_policy=config.l1_eviction_policy
        )

        # Circuit breaker
        self.circuit_breaker = CircuitBreaker(
            threshold=config.circuit_breaker_threshold,
            timeout=config.circuit_breaker_timeout
        )

        # Reconnection state
        self.reconnect_task = None
        self.reconnect_attempts = 0

        # Metrics
        self.metrics = {
            "redis_hits": 0,
            "redis_misses": 0,
            "redis_errors": 0,
            "reconnections": 0,
            "total_operations": 0,
            "l1_hits": 0,
            "l2_hits": 0,
            "write_behinds": 0
        }

        # Initialize connection
        asyncio.create_task(self._initialize())

    async def _initialize(self) -> None:
        """Initialize Redis connection pool."""
        await self._connect()

    async def _connect(self) -> None:
        """Connect to Redis with connection pooling."""
        try:

            self.connection_pool = redis.ConnectionPool(
                host=self.config.redis_host,
                port=self.config.redis_port,
                db=self.config.redis_db,
                password=self.config.redis_password,
                min_connections=self.config.pool_min_size,
                max_connections=self.config.pool_max_size,
                retry_on_timeout=True,
                socket_timeout=self.config.pool_timeout,
                socket_connect_timeout=self.config.pool_timeout
            )

            self.redis_client = redis.Redis(connection_pool=self.connection_pool)

            # Test connection
            await self.redis_client.ping()

            self.connection_status = ConnectionStatus.CONNECTED
            self.reconnect_attempts = 0
            logger.info("Connected to Redis successfully")

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.connection_status = ConnectionStatus.FAILED
            await self._schedule_reconnect()

    async def _schedule_reconnect(self) -> None:
        """Schedule reconnection attempt."""
        if self.reconnect_task and not self.reconnect_task.done():
            return

        self.connection_status = ConnectionStatus.RECONNECTING
        self.reconnect_attempts += 1

        if self.reconnect_attempts > self.config.max_reconnect_attempts:
            logger.error("Max reconnection attempts reached")
            self.connection_status = ConnectionStatus.FAILED
            return

        # Calculate delay with exponential backoff
        delay = min(
            self.config.reconnect_backoff_factor * (2 ** (self.reconnect_attempts - 1)),
            self.config.reconnect_max_delay
        )

        logger.info(f"Scheduling reconnection in {delay:.1f}s (attempt {self.reconnect_attempts})")

        self.reconnect_task = asyncio.create_task(self._reconnect_after_delay(delay))

    async def _reconnect_after_delay(self, delay: float) -> None:
        """Reconnect after delay."""
        await asyncio.sleep(delay)
        await self._connect()

    async def get(self, key: str, use_l1: bool = True, use_l2: bool = True) -> Optional[Any]:
        """Get value from cache (L1 then L2).

        Args:
            key: Cache key
            use_l1: Whether to check L1 cache
            use_l2: Whether to check L2 (Redis) cache

        Returns:
            Cached value or None
        """
        self.metrics["total_operations"] += 1

        # Try L1 cache first
        if use_l1:
            value = await self.l1_cache.get(key)
            if value is not None:
                self.metrics["l1_hits"] += 1
                return value

        # Try L2 cache
        if use_l2 and self.connection_status == ConnectionStatus.CONNECTED:
            try:
                value = await self.circuit_breaker.call(self._get_from_redis, key)
                if value is not None:
                    # Promote to L1
                    if use_l1:
                        await self.l1_cache.set(key, value, self.config.l1_ttl_seconds)
                    self.metrics["l2_hits"] += 1
                    self.metrics["redis_hits"] += 1
                    return value
                else:
                    self.metrics["redis_misses"] += 1

            except Exception as e:
                logger.warning(f"Redis get failed: {e}")
                self.metrics["redis_errors"] += 1

        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
        use_l1: bool = True,
        use_l2: bool = True,
        write_behind: bool = False
    ) -> None:
        """Set value in cache (L1 and L2).

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live
            use_l1: Whether to store in L1 cache
            use_l2: Whether to store in L2 (Redis) cache
            write_behind: If True, write to L2 asynchronously
        """
        self.metrics["total_operations"] += 1

        # Store in L1
        if use_l1:
            await self.l1_cache.set(key, value, ttl_seconds or self.config.l1_ttl_seconds)

        # Store in L2
        if use_l2 and self.connection_status == ConnectionStatus.CONNECTED:
            if write_behind:
                # Async write-behind
                asyncio.create_task(self._write_behind(key, value, ttl_seconds))
                self.metrics["write_behinds"] += 1
            else:
                try:
                    await self.circuit_breaker.call(self._set_to_redis, key, value, ttl_seconds)
                except Exception as e:
                    logger.warning(f"Redis set failed: {e}")
                    self.metrics["redis_errors"] += 1

    async def delete(self, key: str, use_l1: bool = True, use_l2: bool = True) -> bool:
        """# SQL removed: Delete key from cache.

        Args:
            key: Cache key
            use_l1: Whether to delete from L1 cache
            use_l2: Whether to delete from L2 (Redis) cache

        Returns:
            True if key was deleted
        """
        self.metrics["total_operations"] += 1
        deleted = False

        # Delete from L1
        if use_l1:
            if await self.l1_cache.delete(key):
                deleted = True

        # Delete from L2
        if use_l2 and self.connection_status == ConnectionStatus.CONNECTED:
            try:
                result = await self.circuit_breaker.call(self._delete_from_redis, key)
                if result:
                    deleted = True
            except Exception as e:
                logger.warning(f"Redis delete failed: {e}")
                self.metrics["redis_errors"] += 1

        return deleted

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        # Check L1 first
        if await self.l1_cache.get(key) is not None:
            return True

        # Check L2
        if self.connection_status == ConnectionStatus.CONNECTED:
            try:
                return await self.circuit_breaker.call(self._exists_in_redis, key)
            except Exception:
                return False

        return False

    async def get_many(self,
        keys: List[str],
        use_l1: bool = True,
        use_l2: bool = True) -> Dict[str,
        Any]:
        """Get multiple values from cache.

        Args:
            keys: List of cache keys
            use_l1: Whether to check L1 cache
            use_l2: Whether to check L2 cache

        Returns:
            Dictionary of key-value pairs
        """
        results = {}
        missing_keys = []

        # Check L1 cache
        if use_l1:
            for key in keys:
                value = await self.l1_cache.get(key)
                if value is not None:
                    results[key] = value
                    self.metrics["l1_hits"] += 1
                else:
                    missing_keys.append(key)
        else:
            missing_keys = keys

        # Check L2 cache for missing keys
        if use_l2 and missing_keys and self.connection_status == ConnectionStatus.CONNECTED:
            try:
                l2_results = await self.circuit_breaker.call(self._mget_from_redis, missing_keys)
                for key, value in l2_results.items():
                    if value is not None:
                        results[key] = value
                        # Promote to L1
                        if use_l1:
                            await self.l1_cache.set(key, value, self.config.l1_ttl_seconds)
                        self.metrics["l2_hits"] += 1
                    else:
                        self.metrics["redis_misses"] += 1

            except Exception as e:
                logger.warning(f"Redis mget failed: {e}")
                self.metrics["redis_errors"] += 1

        return results

    async def set_many(
        self,
        mapping: Dict[str, Any],
        ttl_seconds: Optional[int] = None,
        use_l1: bool = True,
        use_l2: bool = True
    ) -> None:
        """Set multiple values in cache.

        Args:
            mapping: Dictionary of key-value pairs
            ttl_seconds: Time to live
            use_l1: Whether to store in L1 cache
            use_l2: Whether to store in L2 cache
        """
        # Store in L1
        if use_l1:
            for key, value in mapping.items():
                await self.l1_cache.set(key, value, ttl_seconds or self.config.l1_ttl_seconds)

        # Store in L2
        if use_l2 and mapping and self.connection_status == ConnectionStatus.CONNECTED:
            try:
                await self.circuit_breaker.call(self._mset_to_redis, mapping, ttl_seconds)
            except Exception as e:
                logger.warning(f"Redis mset failed: {e}")
                self.metrics["redis_errors"] += 1

    async def _get_from_redis(self, key: str) -> Optional[Any]:
        """Get value from Redis."""
        value = await self.redis_client.get(key)
        if value is None:
            return None

        try:
            return pickle.loads(value)
        except Exception:
            return value.decode('utf-8')

    async def _set_to_redis(self, key: str, value: Any, ttl_seconds: Optional[int]) -> None:
        """Set value in Redis."""
        try:
            serialized = pickle.dumps(value)
        except Exception:
            serialized = str(value).encode()

        if ttl_seconds:
            await self.redis_client.setex(key, ttl_seconds, serialized)
        else:
            await self.redis_client.set(key, serialized)

    async def _delete_from_redis(self, key: str) -> bool:
        """# SQL removed: Delete key from Redis."""
        result = await self.redis_client.delete(key)
        return result > 0

    async def _exists_in_redis(self, key: str) -> bool:
        """Check if key exists in Redis."""
        return await self.redis_client.exists(key) > 0

    async def _mget_from_redis(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from Redis."""
        values = await self.redis_client.mget(keys)
        results = {}

        for key, value in zip(keys, values):
            if value is not None:
                try:
                    results[key] = pickle.loads(value)
                except Exception:
                    results[key] = value.decode('utf-8')

        return results

    async def _mset_to_redis(self, mapping: Dict[str, Any], ttl_seconds: Optional[int]) -> None:
        """Set multiple values in Redis."""
        pipe = self.redis_client.pipeline()

        for key, value in mapping.items():
            try:
                serialized = pickle.dumps(value)
            except Exception:
                serialized = str(value).encode()

            if ttl_seconds:
                pipe.setex(key, ttl_seconds, serialized)
            else:
                pipe.set(key, serialized)

        await pipe.execute()

    async def _write_behind(self, key: str, value: Any, ttl_seconds: Optional[int]) -> None:
        """Write-behind to Redis."""
        try:
            await self._set_to_redis(key, value, ttl_seconds)
        except Exception as e:
            logger.warning(f"Write-behind failed for key {key}: {e}")
            self.metrics["redis_errors"] += 1

    async def clear(self, tier: CacheTier = CacheTier.BOTH) -> None:
        """Clear cache tier(s).

        Args:
            tier: Which tier to clear
        """
        if tier in [CacheTier.L1_MEMORY, CacheTier.BOTH]:
            await self.l1_cache.clear()

        if tier in [CacheTier.L2_REDIS, CacheTier.BOTH] and self.connection_status == ConnectionStatus.CONNECTED:
            try:
                await self.redis_client.flushdb()
            except Exception as e:
                logger.error(f"Failed to clear Redis: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        # Calculate hit rates
        total_redis_ops = self.metrics["redis_hits"] + self.metrics["redis_misses"]
        redis_hit_rate = self.metrics["redis_hits"] / total_redis_ops if total_redis_ops > 0 else 0

        total_ops = self.metrics["total_operations"]
        overall_hit_rate = (self.metrics["l1_hits"] + self.metrics["l2_hits"]) / total_ops if total_ops > 0 else 0

        return {
            "connection": {
                "status": self.connection_status.value,
                "reconnect_attempts": self.reconnect_attempts,
                "reconnections": self.metrics["reconnections"]
            },
            "metrics": {
                **self.metrics,
                "redis_hit_rate": redis_hit_rate,
                "overall_hit_rate": overall_hit_rate
            },
            "l1_cache": self.l1_cache.get_stats(),
            "circuit_breaker": self.circuit_breaker.get_state()
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        health = {
            "status": "healthy",
            "checks": {}
        }

        # Check Redis connection
        if self.connection_status == ConnectionStatus.CONNECTED:
            try:
                await self.redis_client.ping()
                health["checks"]["redis"] = "connected"
            except Exception:
                health["checks"]["redis"] = "error"
                health["status"] = "degraded"
        else:
            health["checks"]["redis"] = self.connection_status.value
            health["status"] = "degraded"

        # Check circuit breaker
        if self.circuit_breaker.state == "open":
            health["checks"]["circuit_breaker"] = "open"
            health["status"] = "degraded"
        else:
            health["checks"]["circuit_breaker"] = "closed"

        # Check L1 cache
        l1_stats = self.l1_cache.get_stats()
        if l1_stats["utilization"] > 0.9:
            health["checks"]["l1_cache"] = "high_utilization"
            health["status"] = "degraded"
        else:
            health["checks"]["l1_cache"] = "ok"

        return health

    async def close(self) -> None:
        """Close connections and cleanup."""
        if self.reconnect_task and not self.reconnect_task.done():
            self.reconnect_task.cancel()

        if self.connection_pool:
            await self.connection_pool.disconnect()

        await self.l1_cache.clear()
        logger.info("Hardened cache client closed")

# Factory function for creating hardened cache client
def create_hardened_cache_client(config: Optional[CacheConfig] = None) -> HardenedCacheClient:
    """Create a hardened cache client.

    Args:
        config: Cache configuration

    Returns:
        HardenedCacheClient instance
    """
    return HardenedCacheClient(config or CacheConfig())
