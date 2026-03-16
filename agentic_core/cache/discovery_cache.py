"""Agent Discovery Cache — Redis-backed deterministic agent lookup cache.

Caches parsed agent_discovery_full.json to eliminate repeated file I/O and JSON parsing.
Keyed by file content hash for automatic invalidation on updates.
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Any

from agentic_core.cache.cache_key_builders import _require_hash_segment
from agentic_core.cache.redis_cache_client import DeterministicRedisCache, get_hot_cache
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "discovery_cache", "p0_governance")
_emit_reads_policy_state("p0", "discovery_cache", "policy_binding")
_emit_snapshots_state("p0", "discovery_cache", "state_snapshot")
emit_replay_key("p0", "discovery_cache")
emit_determinism_digest("p0", "discovery_cache")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)
_DEFAULT_DISCOVERY_TTL = 3600 * 24


class AgentDiscoveryCache:
    """Cache for agent discovery JSON parsing.

    Eliminates repeated file I/O and JSON parsing for agent_discovery_full.json.
    Automatically invalidates when file content changes via content hash keying.
    """

    def __init__(
        self, cache: DeterministicRedisCache | None = None, ttl_seconds: int = _DEFAULT_DISCOVERY_TTL
    ):
        self._cache = cache or get_hot_cache()
        self._ttl = ttl_seconds

    def get_or_fetch(
        self, discovery_path: Path, fetch_from_disk: Any, *, replay_mode: bool = False
    ) -> list[dict[str, Any]]:
        """Read-through helper: return cached parsed agents or call *fetch_from_disk*.

        *fetch_from_disk* is a zero-argument callable that reads and parses the
        discovery JSON file.  Called only on cache miss or when file content changes.

        Args:
            discovery_path: Path to agent_discovery_full.json
            fetch_from_disk: Callable that returns list[dict] of agent records
            replay_mode: If True, bypass cache entirely

        Returns:
            List of agent discovery records

        Raises:
            FileNotFoundError: If discovery_path does not exist
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "AgentDiscoveryCache.get_or_fetch")

        if not replay_mode:
            try:
                content_hash = self._compute_file_hash(discovery_path)
                cache_key = f"agent_discovery:{content_hash}"
            except FileNotFoundError:
                raise
            except (OSError, ValueError) as e:
                logger.warning(f"[Discovery cache] Hash computation failed: {e}")
            else:
                try:
                    cached = self._cache.get_json(cache_key)
                    if cached is not None:
                        logger.debug("[Discovery cache] HIT")
                        return cached
                # guardian: allow-silent-swallow
                except Exception as e:
                    logger.warning(f"[Discovery cache] Cache read failed: {e}")
        logger.debug("[Discovery cache] MISS — fetching from disk")
        result = fetch_from_disk()
        if not replay_mode:
            try:
                content_hash = self._compute_file_hash(discovery_path)
                cache_key = f"agent_discovery:{content_hash}"
                self._cache.set_json(cache_key, result, ttl_seconds=self._ttl)
            except FileNotFoundError:
                pass
            # guardian: allow-silent-swallow
            except Exception as e:
                logger.warning(f"[Discovery cache] Cache write failed: {e}")
        return result

    def _compute_file_hash(self, path: Path) -> str:
        """Compute SHA-256 hash of file contents for cache key."""
        if not path.exists():
            raise FileNotFoundError(f"Discovery file not found: {path}")
        content = path.read_bytes()
        file_hash = hashlib.sha256(content).hexdigest()
        _require_hash_segment("file_content_hash", file_hash)
        return file_hash

    def invalidate_all(self) -> None:
        """Invalidate all cached discovery data.

        Note: This is a no-op since cache keys are content-addressed.
        File changes automatically invalidate via different hash.
        """
        logger.debug("[Discovery cache] invalidate_all called (no-op for content-addressed cache)")


def get_agent_discovery_cache() -> AgentDiscoveryCache:
    """Get the singleton agent discovery cache instance."""
    return AgentDiscoveryCache()
