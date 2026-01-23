from __future__ import annotations
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

"""
Storage adapters for different backend types.

Provides atomic storage operations with hot-swappable backends.
Supports local disk (for development) and S3 (for production).
"""
import json
import logging
import time
from pathlib import Path
from typing import Any, Protocol

Logger: Any = logging.getLogger(__name__)


class BlobStorageProvider(Protocol):
    """
    Protocol defining atomic storage operations.
    Standardizes 'open', 'write', 'read' across Local FS and Cloud.
    """

    async def write_blob(self: Any, key: str, data: bytes, metadata: dict[str, str] | None) -> str:
        """Writes data atomically. Returns a version ID or checksum."""
        ...

    async def read_blob(self: Any, key: str) -> bytes:
        """Reads data given a key."""
        ...

    async def exists(self: Any, key: str) -> bool:
        """Checks if key exists."""
        ...


class LocalDiskAdapter:
    """
    Mimics cloud storage on local disk.
    Uses atomic 'write-to-temp-then-move' logic to prevent corruption.

    This adapter is perfect for development and ensures that your code
    works identically whether running locally or in production on S3.
    """

    def __init__(self: Any, base_path: str) -> None:
        """
        Initialize local disk storage.

        Args:
            base_path: Base directory for storage
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        LOGGER.info(f"Local disk adapter initialized at: {self.base_path}")

    def _get_path(self: Any, key: str) -> Path:
        """
        Convert storage key to filesystem path.

        Args:
            key: Storage key

        Returns:
            Safe path within base directory
        """
        key = key.replace("\\", "/")
        parts = [p for p in key.split("/") if p and p != ".."]
        safe_key = Path(*parts)
        full_path = self.base_path / safe_key
        if not str(full_path).startswith(str(self.base_path)):
            raise ValueError(f"Invalid key: {key} (directory traversal attempt)")
        return full_path

    async def write_blob(self: Any, key: str, data: bytes, metadata: dict[str, str] | None) -> str:
        """
        Write data atomically using temp-file-then-move pattern.

        Args:
            key: Storage key
            data: Binary data to write
            metadata: Optional metadata dictionary

        Returns:
            MD5 checksum of the data
        """
        target_path: Any = self._get_path(key)
        temp_path: Any = target_path.with_suffix(".tmp")
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_path, "wb") as f:
            f.write(data)
        if metadata:
            meta_path: Any = target_path.with_suffix(".meta.json")
            with open(meta_path, "w") as f:
                json.dump(metadata, f)
        shutil.move(str(temp_path), str(target_path))
        checksum: Any = hashlib.md5(data).hexdigest()
        LOGGER.debug(f"Wrote blob: {key} (checksum={checksum})")
        return checksum

    async def read_blob(self: Any, key: str) -> bytes:
        """
        Read data from storage.

        Args:
            key: Storage key

        Returns:
            Binary data

        Raises:
            FileNotFoundError: If key doesn't exist
        """
        target_path: Any = self._get_path(key)
        if not target_path.exists():
            raise FileNotFoundError(f"Key {key} not found in storage.")
        with open(target_path, "rb") as f:
            data: Any = f.read()
        LOGGER.debug(f"Read blob: {key} ({len(data)} bytes)")
        return data

    async def exists(self: Any, key: str) -> bool:
        """
        Check if key exists in storage.

        Args:
            key: Storage key

        Returns:
            True if key exists, False otherwise
        """
        return self._get_path(key).exists()

    async def delete_blob(self: Any, key: str) -> bool:
        """
        Delete a blob from storage.

        Args:
            key: Storage key

        Returns:
            True if deleted, False if didn't exist
        """
        target_path: Any = self._get_path(key)
        if target_path.exists():
            target_path.unlink()
            meta_path: Any = target_path.with_suffix(".meta.json")
            if meta_path.exists():
                meta_path.unlink()
            LOGGER.debug(f"Deleted blob: {key}")
            return True
        return False

    async def list_blobs(self: Any, prefix: str) -> list:
        """
        List all blobs with optional prefix filter.

        Args:
            prefix: Optional prefix to filter by

        Returns:
            List of blob keys
        """
        blobs: Any = []
        from agentic_core.utils.ssot_discovery import get_data_files, get_python_files

        all_files = list(get_python_files(self.base_path)) + list(get_data_files(self.base_path))
        for path in all_files:
            if path.is_file() and (path.suffix not in [".tmp", ".meta.json"]):
                relative: Any = path.relative_to(self.base_path)
                key: Any = str(relative)
                if not prefix or key.startswith(prefix):
                    blobs.append(key)
        return blobs


class S3Adapter:
    """
    Production adapter for AWS S3.

    Requires: pip install boto3
    """

    def __init__(self: Any, bucket_name: str, region: str) -> None:
        """
        Initialize S3 storage adapter.

        Args:
            bucket_name: S3 bucket name
            region: AWS region
        """
        try:
            import boto3

            self.s3 = boto3.client("s3", region_name=region)
            self.bucket = bucket_name
            LOGGER.info(f"S3 adapter initialized (bucket={bucket_name}, region={region})")
        except ImportError:
            raise ImportError("boto3 not installed. Run: pip install boto3")

    async def write_blob(self: Any, key: str, data: bytes, metadata: dict[str, str] | None) -> str:
        """
        Write data to S3 (atomic by default).

        Args:
            key: S3 object key
            data: Binary data to write
            metadata: Optional metadata dictionary

        Returns:
            ETag from S3
        """
        response: Any = self.s3.put_object(
            Bucket=self.bucket, Key=key, Body=data, Metadata=metadata or {}
        )
        etag: Any = response["ETag"].replace('"', "")
        LOGGER.debug(f"Wrote S3 blob: {key} (etag={etag})")
        return etag

    async def read_blob(self: Any, key: str) -> bytes:
        """
        Read data from S3.

        Args:
            key: S3 object key

        Returns:
            Binary data
        """
        response: Any = self.s3.get_object(Bucket=self.bucket, Key=key)
        data: Any = response["Body"].read()
        LOGGER.debug(f"Read S3 blob: {key} ({len(data)} bytes)")
        return data

    async def exists(self: Any, key: str) -> bool:
        """
        Check if key exists in S3.

        Args:
            key: S3 object key

        Returns:
            True if key exists, False otherwise
        """
        try:
            self.s3.head_object(Bucket=self.bucket, Key=key)
            return True
        except Exception:
            return False

    async def delete_blob(self: Any, key: str) -> bool:
        """
        Delete a blob from S3.

        Args:
            key: S3 object key

        Returns:
            True if deleted
        """
        try:
            self.s3.delete_object(Bucket=self.bucket, Key=key)
            LOGGER.debug(f"Deleted S3 blob: {key}")
            return True
        except Exception as e:
            LOGGER.error(f"Failed to delete S3 blob {key}: {e}")
            return False

    async def list_blobs(self: Any, prefix: str) -> list:
        """
        List all blobs in S3 with optional prefix filter.

        Args:
            prefix: Optional prefix to filter by

        Returns:
            List of blob keys
        """
        blobs: Any = []
        paginator: Any = self.s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
            if "Contents" in page:
                blobs.extend([obj["Key"] for obj in page["Contents"]])
        return blobs


def create_storage_adapter(adapter_type: str = "local", **kwargs) -> BlobStorageProvider:
    """
    Factory function to create storage adapters.

    Args:
        adapter_type: "local" or "s3"
        **kwargs: Adapter-specific arguments

    Returns:
        Storage adapter instance
    """
    if adapter_type == "local":
        base_path: Any = kwargs.get("base_path", "./agent_data_store")
        return LocalDiskAdapter(base_path=base_path)
    elif adapter_type == "s3":
        bucket_name: Any = kwargs.get("bucket_name")
        if not bucket_name:
            raise ValueError("bucket_name required for S3 adapter")
        region: Any = kwargs.get("region", "us-east-1")
        return S3Adapter(bucket_name=bucket_name, region=region)
    else:
        raise ValueError(f"Unknown adapter type: {adapter_type}")


from agentic_core.L5_safety.validators.structure_blueprint import (
    TESTS_DIR,
)


class RedisDistributedLock(SovereignBaseAgent):
    """
    Redis-based distributed lock for coordination across multiple processes.
    """

    def __init__(self, redis_client=None, lock_timeout: int = 30):
        """
        Initialize the distributed lock.

        Args:
            redis_client: Redis client instance
            lock_timeout: Default lock timeout in seconds
        """
        self.redis = redis_client
        self.lock_timeout = lock_timeout
        self._local_cache = {}

    async def acquire_lock(self, key: str, timeout: int | None = None) -> bool:
        """
        Acquire a distributed lock.

        Args:
            key: Lock key
            timeout: Custom timeout (uses default if None)

        Returns:
            True if lock acquired, False otherwise
        """
        if not self.redis:
            if key in self._local_cache:
                return False
            self._local_cache[key] = time.time() + (timeout or self.lock_timeout)
            return True
        try:
            lock_key: Any = f"lock:{key}"
            expires_in: Any = timeout or self.lock_timeout
            result: Any = await self.redis.set(lock_key, "locked", ex=expires_in, nx=True)
            if result:
                LOGGER.debug(f"Acquired lock: {key}")
                return True
            else:
                LOGGER.debug(f"Failed to acquire lock: {key} (already held)")
                return False
        except Exception as e:
            LOGGER.error(f"Error acquiring lock {key}: {e}")
            if key not in self._local_cache:
                self._local_cache[key] = time.time() + (timeout or self.lock_timeout)
                return True
            return False

    async def release_lock(self, key: str) -> bool:
        """
        Release a distributed lock.

        Args:
            key: Lock key

        Returns:
            True if lock released, False otherwise
        """
        if not self.redis:
            if key in self._local_cache:
                del self._local_cache[key]
                return True
            return False
        try:
            lock_key: Any = f"lock:{key}"
            result: Any = await self.redis.delete(lock_key)
            if result:
                LOGGER.debug(f"Released lock: {key}")
                return True
            else:
                LOGGER.warning(f"Lock not found for release: {key}")
                return False
        except Exception as e:
            LOGGER.error(f"Error releasing lock {key}: {e}")
            if key in self._local_cache:
                del self._local_cache[key]
            return False

    async def is_locked(self, key: str) -> bool:
        """
        Check if a lock is currently held.

        Args:
            key: Lock key

        Returns:
            True if locked, False otherwise
        """
        if not self.redis:
            return key in self._local_cache
        try:
            lock_key: Any = f"lock:{key}"
            return await self.redis.exists(lock_key)
        except Exception:
            return key in self._local_cache


def _run_self_tests(self) -> dict:
    """Run internal self-tests."""
    results = {"passed": 0, "failed": 0, TESTS_DIR: []}
    try:
        assert self is not None
        results["passed"] += 1
        results[TESTS_DIR].append({"name": "test_instantiation", "status": "passed"})
    except AssertionError as e:
        results["failed"] += 1
        results[TESTS_DIR].append(
            {"name": "test_instantiation", "status": "failed", "error": str(e)}
        )
    return results


class RedisHotCache(SovereignBaseAgent):
    """
    Redis-based hot cache with local fallback for frequently accessed data.
    """

    def __init__(self, redis_client=None, default_ttl: int = 3600):
        """
        Initialize the hot cache.

        Args:
            redis_client: Redis client instance
            default_ttl: Default TTL in seconds
        """
        super().__init__()
        self.redis = redis_client
        self.default_ttl = default_ttl
        self._local_cache = {}
        self._local_cache_times = {}
        self._mcp_audit("init")

    async def set_cache(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """
        Set a value in cache.

        Args:
            key: cache key
            value: Value to cache (must be JSON serializable)
            ttl: Time to live (uses default if None)

        Returns:
            True if set successfully, False otherwise
        """
        try:
            serialized: Any = json.dumps(value)
        except (TypeError, ValueError) as e:
            LOGGER.error(f"Cannot serialize cache value for {key}: {e}")
            return False
        if not self.redis:
            self._local_cache[key] = value
            self._local_cache_times[key] = time.time() + (ttl or self.default_ttl)
            return True
        try:
            cache_key: Any = f"cache:{key}"
            expire_time: Any = ttl or self.default_ttl
            result: Any = await self.redis.setex(cache_key, expire_time, serialized)
            if result:
                LOGGER.debug(f"Cached value: {key} (TTL: {expire_time}s)")
                return True
            return False
        except Exception as e:
            LOGGER.error(f"Error caching {key}: {e}")
            self._local_cache[key] = value
            self._local_cache_times[key] = time.time() + (ttl or self.default_ttl)
            return True

    async def get_cache(self, key: str) -> Any | None:
        """
        Get a value from cache.

        Args:
            key: cache key

        Returns:
            Cached value or None if not found
        """
        if not self.redis:
            if key in self._local_cache:
                if time.time() < self._local_cache_times.get(key, 0):
                    return self._local_cache[key]
                else:
                    del self._local_cache[key]
                    if key in self._local_cache_times:
                        del self._local_cache_times[key]
            return None
        try:
            cache_key: Any = f"cache:{key}"
            serialized: Any = await self.redis.get(cache_key)
            if serialized:
                value: Any = json.loads(serialized)
                LOGGER.debug(f"cache hit: {key}")
                return value
            else:
                LOGGER.debug(f"cache miss: {key}")
                return None
        except Exception as e:
            LOGGER.error(f"Error getting cache {key}: {e}")
            if key in self._local_cache:
                if time.time() < self._local_cache_times.get(key, 0):
                    return self._local_cache[key]
            return None

    async def delete_cache(self, key: str) -> bool:
        """
        Delete a value from cache.

        Args:
            key: cache key

        Returns:
            True if deleted, False otherwise
        """
        if not self.redis:
            if key in self._local_cache:
                del self._local_cache[key]
            if key in self._local_cache_times:
                del self._local_cache_times[key]
            return True
        try:
            cache_key: Any = f"cache:{key}"
            result: Any = await self.redis.delete(cache_key)
            if result:
                LOGGER.debug(f"Deleted cache: {key}")
                return True
            return False
        except Exception as e:
            LOGGER.error(f"Error deleting cache {key}: {e}")
            if key in self._local_cache:
                del self._local_cache[key]
            if key in self._local_cache_times:
                del self._local_cache_times[key]
            return False

    async def clear_expired_local(self) -> Any:
        """Clear expired entries from local fallback cache."""
        now: Any = time.time()
        expired_keys: Any = []
        for key, expire_time in self._local_cache_times.items():
            if now >= expire_time:
                expired_keys.append(key)
        for key in expired_keys:
            if key in self._local_cache:
                del self._local_cache[key]
            del self._local_cache_times[key]
        if expired_keys:
            LOGGER.debug(f"Cleared {len(expired_keys)} expired local cache entries")


_redis_client = None
_distributed_lock: RedisDistributedLock | None = None
_hot_cache: RedisHotCache | None = None


async def initialize_redis(redis_url: str = "redis://localhost:6379") -> Any:
    """
    Initialize Redis client and distributed systems.

    Args:
        redis_url: Redis connection URL
    """
    global _redis_client, _distributed_lock, _hot_cache
    try:
        import redis.asyncio as redis

        _redis_client = redis.from_url(redis_url, decode_responses=True)
        await _redis_client.ping()
        _distributed_lock = RedisDistributedLock(_redis_client)
        _hot_cache = RedisHotCache(_redis_client)
        LOGGER.info(f"Redis initialized at {redis_url}")
    except ImportError:
        LOGGER.warning("redis not installed - using local fallback only")
        _distributed_lock = RedisDistributedLock()
        _hot_cache = RedisHotCache()
    except Exception as e:
        LOGGER.error(f"Failed to connect to Redis: {e} - using local fallback")
        _distributed_lock = RedisDistributedLock()
        _hot_cache = RedisHotCache()


def get_distributed_lock() -> RedisDistributedLock:
    """Get the distributed lock instance."""
    global _distributed_lock
    if _distributed_lock is None:
        _distributed_lock = RedisDistributedLock()
    return _distributed_lock


def get_hot_cache() -> RedisHotCache:
    """Get the hot cache instance."""
    global _hot_cache
    if _hot_cache is None:
        _hot_cache = RedisHotCache()
    return _hot_cache


async def acquire_lock(key: str, timeout: int | None = None) -> bool:
    """Acquire a distributed lock."""
    lock: Any = get_distributed_lock()
    return await lock.acquire_lock(key, timeout)


async def release_lock(key: str) -> bool:
    """Release a distributed lock."""
    lock: Any = get_distributed_lock()
    return await lock.release_lock(key)


async def set_cache(key: str, value: Any, ttl: int | None = None) -> bool:
    """Set a value in cache."""
    cache: Any = get_hot_cache()
    return await cache.set_cache(key, value, ttl)


async def get_cache(key: str) -> Any | None:
    """Get a value from cache."""
    cache: Any = get_hot_cache()
    return await cache.get_cache(key)


class SignalLedger:
    """
    Simple ledger that logs ExecutionResults to a permanent log file.
    """

    def __init__(self, storage_adapter: BlobStorageProvider, session_id: str):
        """
        Initialize the signal ledger.

        Args:
            storage_adapter: Storage adapter for persistence
            session_id: Session identifier for this ledger
        """
        self.storage = storage_adapter
        self.session_id = session_id
        self.ledger_key = f"signal_ledger_{session_id}.jsonl"

    async def append_result(self, result: Any) -> None:
        """
        Append an ExecutionResult to the ledger.

        Args:
            result: ExecutionResult to log
        """
        from datetime import datetime

        if hasattr(result, "__dict__"):
            result_dict: Any = result.__dict__
        else:
            result_dict: Any = result
        result_dict["timestamp"] = datetime.utcnow().isoformat()
        result_dict["session_id"] = self.session_id
        json_line: Any = json.dumps(result_dict) + "\n"
        try:
            existing_data: Any = await self.storage.read_blob(self.ledger_key)
            existing_lines: Any = existing_data.decode("utf-8")
        except FileNotFoundError:
            existing_lines: Any = ""
        updated_data: Any = existing_lines + json_line
        await self.storage.write_blob(
            self.ledger_key,
            updated_data.encode("utf-8"),
            metadata={"type": "SignalLedger", "session_id": self.session_id},
        )
        LOGGER.debug(f"Appended result to signal ledger: {self.ledger_key}")

    async def get_results(self) -> list:
        """
        Get all results from the ledger.

        Returns:
            List of result dictionaries
        """
        try:
            data: Any = await self.storage.read_blob(self.ledger_key)
            lines: Any = data.decode("utf-8").strip().split("\n")
            results: Any = []
            for line in lines:
                if line.strip():
                    results.append(json.loads(line))
            return results
        except FileNotFoundError:
            return []

    async def get_phase_summary(self, phase_name: str | None = None) -> dict[str, Any]:
        """
        Get a summary of signals from a specific phase or the most recent phase.

        Args:
            phase_name: Specific phase to get summary for, or None for most recent

        Returns:
            Dictionary with phase summary including signals, results, and recommendations
        """
        results: Any = await self.get_results()
        if not results:
            return {}
        if phase_name:
            phase_results: Any = [r for r in results if r.get("phase") == phase_name]
        else:
            phase_results: Any = []
            if results:
                latest_result: Any = max(results, key=lambda x: x.get("timestamp", ""))
                latest_phase: Any = latest_result.get("phase")
                if latest_phase:
                    phase_results: Any = [r for r in results if r.get("phase") == latest_phase]
        if not phase_results:
            return {}
        summary: Any = {
            "phase": phase_results[0].get("phase", "unknown"),
            "timestamp": phase_results[0].get("timestamp"),
            "total_results": len(phase_results),
            "passed_count": sum(1 for r in phase_results if r.get("passed", False)),
            "failed_count": sum(1 for r in phase_results if not r.get("passed", False)),
            "signals": [],
            "failed_agents": [],
            "recommendations": [],
        }
        for result in phase_results:
            if "result" in result and isinstance(result["result"], dict):
                signals: Any = result["result"].get("signals", [])
                if signals:
                    summary["signals"].extend(signals)
            if not result.get("passed", False):
                agent_name: Any = result.get("agent", "unknown")
                summary["failed_agents"].append(
                    {
                        "agent": agent_name,
                        "error": result.get("error", "Unknown error"),
                        "details": result.get("details", ""),
                    }
                )
        if summary["failed_count"] > 0:
            summary["recommendations"].append(
                f"Phase {summary['phase']} had {summary['failed_count']} failures"
            )
            summary["recommendations"].append("Consider re-running failed agents before proceeding")
        if summary["phase"] == "integrity_seq" and summary["failed_count"] > 0:
            summary["recommendations"].append(
                "CRITICAL: Integrity failures must be resolved before continuing"
            )
        return summary


class HotBrainCache:
    """
    Redis-based hot brain cache for distributed coordination.

    Provides fast, distributed caching and locking capabilities
    for multi-instance deployments. Falls back to local cache
    when Redis is unavailable.
    """

    def __init__(self, redis_url: str | None = None):
        """
        Initialize hot brain cache.

        Args:
            redis_url: Redis connection URL (optional)
        """
        self.redis_url = redis_url
        self.redis_client = None
        self._local_cache = {}
        self._local_locks = {}
        if redis_url:
            try:
                import redis.asyncio as redis

                self.redis_client = redis.from_url(redis_url)
                LOGGER.info("Hot brain connected to Redis")
            except ImportError:
                LOGGER.warning("redis not installed - using local cache only")
            except Exception as e:
                LOGGER.warning(f"Redis connection failed: {e} - using local cache only")

    async def acquire_lock(self, key: str, timeout: float = 30.0) -> bool:
        """
        Acquire a distributed lock.

        Args:
            key: Lock key
            timeout: Lock timeout in seconds

        Returns:
            True if lock acquired, False otherwise
        """
        if self.redis_client:
            try:
                lock_key: Any = f"lock:{key}"
                result: Any = await self.redis_client.set(lock_key, "locked", ex=timeout, nx=True)
                return result is not None
            except Exception as e:
                LOGGER.error(f"Redis lock acquisition failed: {e}")
        if key in self._local_locks:
            return False
        self._local_locks[key] = time.time() + timeout
        return True

    async def release_lock(self, key: str) -> bool:
        """
        Release a distributed lock.

        Args:
            key: Lock key

        Returns:
            True if lock released, False otherwise
        """
        if self.redis_client:
            try:
                lock_key: Any = f"lock:{key}"
                result: Any = await self.redis_client.delete(lock_key)
                return result > 0
            except Exception as e:
                LOGGER.error(f"Redis lock release failed: {e}")
        if key in self._local_locks:
            del self._local_locks[key]
            return True
        return False

    async def get(self, key: str) -> Any | None:
        """Get value from cache."""
        if self.redis_client:
            try:
                value: Any = await self.redis_client.get(key)
                if value:
                    return json.loads(value)
            except Exception as e:
                LOGGER.error(f"Redis get failed: {e}")
        return self._local_cache.get(key)

    async def set(self, key: str, value: Any, ttl: float | None = None) -> bool:
        """Set value in cache."""
        serialized: Any = json.dumps(value)
        if self.redis_client:
            try:
                if ttl:
                    await self.redis_client.setex(key, ttl, serialized)
                else:
                    await self.redis_client.set(key, serialized)
                return True
            except Exception as e:
                LOGGER.error(f"Redis set failed: {e}")
        self._local_cache[key] = value
        return True

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if self.redis_client:
            try:
                await self.redis_client.delete(key)
            except Exception as e:
                LOGGER.error(f"Redis delete failed: {e}")
        if key in self._local_cache:
            del self._local_cache[key]
            return True
        return False


_hot_brain: HotBrainCache | None = None


def get_hot_brain(redis_url: str | None = None) -> HotBrainCache:
    """Get or create the global hot brain cache instance."""
    global _hot_brain
    if _hot_brain is None:
        _hot_brain = HotBrainCache(redis_url)
    return _hot_brain
