"""Config File Parse Cache — Redis-backed cache for parsed YAML/JSON config files.

Caches parsed configuration files to eliminate repeated file I/O and parsing.
Keyed by file path + content hash for automatic invalidation on file changes.
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Any

from agentic_core.cache.cache_key_builders import _require_hash_segment
from agentic_core.cache.redis_cache_client import DeterministicRedisCache, get_hot_cache

logger = logging.getLogger(__name__)

_DEFAULT_CONFIG_TTL = 3600 * 24  # 24 hours


class ConfigFileCache:
    """Cache for parsed YAML/JSON configuration files.

    Eliminates repeated file I/O and parsing for the same config files.
    Automatically invalidates when file content changes via content hash keying.
    """

    def __init__(
        self,
        cache: DeterministicRedisCache | None = None,
        ttl_seconds: int = _DEFAULT_CONFIG_TTL,
    ):
        self._cache = cache or get_hot_cache()
        self._ttl = ttl_seconds

    def get_or_fetch(
        self,
        config_path: Path,
        fetch_from_disk: Any,
        *,
        replay_mode: bool = False,
    ) -> dict[str, Any]:
        """Read-through helper: return cached parsed config or call *fetch_from_disk*.

        *fetch_from_disk* is a zero-argument callable that reads and parses the
        config file.  Called only on cache miss or when file content changes.

        Args:
            config_path: Path to YAML/JSON config file
            fetch_from_disk: Callable that returns parsed config dict
            replay_mode: If True, bypass cache entirely

        Returns:
            Parsed configuration dict

        Raises:
            FileNotFoundError: If config_path does not exist
        """
        if not replay_mode:
            try:
                content_hash = self._compute_file_hash(config_path)
                cache_key = f"config:{config_path.name}:{content_hash}"
                cached = self._cache.get_json(cache_key)
                if cached is not None:
                    logger.debug(f"[Config cache] HIT for {config_path.name}")
                    return cached
            except FileNotFoundError:
                raise
            except Exception as e:
                logger.warning(f"[Config cache] Cache read failed: {e}")

        logger.debug(f"[Config cache] MISS for {config_path.name} — parsing from disk")
        result = fetch_from_disk()

        if not replay_mode:
            try:
                content_hash = self._compute_file_hash(config_path)
                cache_key = f"config:{config_path.name}:{content_hash}"
                self._cache.set_json(cache_key, result, ttl_seconds=self._ttl)
            except FileNotFoundError:
                pass  # File may have been deleted after fetch
            except Exception as e:
                logger.warning(f"[Config cache] Cache write failed: {e}")

        return result

    def _compute_file_hash(self, path: Path) -> str:
        """Compute SHA-256 hash of file contents for cache key."""
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        content = path.read_bytes()
        file_hash = hashlib.sha256(content).hexdigest()
        _require_hash_segment("file_content_hash", file_hash)
        return file_hash

    def invalidate(self, config_path: Path) -> None:
        """Invalidate cached config for specific file.

        Note: This is a no-op since cache keys are content-addressed.
        File changes automatically invalidate via different hash.
        """
        logger.debug(
            f"[Config cache] invalidate called for {config_path.name} (no-op for content-addressed cache)"
        )


def get_config_file_cache() -> ConfigFileCache:
    """Get the singleton config file cache instance."""
    return ConfigFileCache()
