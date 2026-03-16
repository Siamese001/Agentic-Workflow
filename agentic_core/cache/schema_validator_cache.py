"""JSON Schema Validator Cache — Redis-backed cache for compiled schema validators.

Caches compiled JSON schema validators to eliminate repeated schema compilation.
Keyed by schema content hash for automatic invalidation on schema changes.
"""

from __future__ import annotations

import hashlib
import json
import logging
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

_emit_applies_guardrail("p0", "schema_validator_cache", "p0_governance")
_emit_reads_policy_state("p0", "schema_validator_cache", "policy_binding")
_emit_snapshots_state("p0", "schema_validator_cache", "state_snapshot")
emit_replay_key("p0", "schema_validator_cache")
emit_determinism_digest("p0", "schema_validator_cache")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)
_DEFAULT_SCHEMA_TTL = 3600 * 24


class SchemaValidatorCache:
    """Cache for compiled JSON schema validators.

    Eliminates repeated schema compilation for the same schema definitions.
    Automatically invalidates when schema changes via content hash keying.
    """

    def __init__(self, cache: DeterministicRedisCache | None = None, ttl_seconds: int = _DEFAULT_SCHEMA_TTL):
        self._cache = cache or get_hot_cache()
        self._ttl = ttl_seconds

    def get_or_fetch(self, schema: dict[str, Any], fetch_validator: Any, *, replay_mode: bool = False) -> Any:
        """Read-through helper: return cached validator result or call *fetch_validator*.

        *fetch_validator* is a zero-argument callable that compiles and returns
        a validator function or validation result.  Called only on cache miss.

        Args:
            schema: JSON schema dict to validate against
            fetch_validator: Callable that returns compiled validator or validation result
            replay_mode: If True, bypass cache entirely

        Returns:
            Compiled validator or validation result

        Raises:
            ValueError: If schema is empty
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SchemaValidatorCache.get_or_fetch")

        if not schema:
            raise ValueError("Schema dict must not be empty")
        if not replay_mode:
            try:
                schema_hash = self._compute_schema_hash(schema)
                cache_key = f"schema_validator:{schema_hash}"
                cached = self._cache.get_json(cache_key)
                if cached is not None:
                    logger.debug("[Schema validator cache] HIT")
                    return cached
            except ValueError:
                raise
            # guardian: allow-silent-swallow
            except Exception as e:
                logger.warning(f"[Schema validator cache] Cache read failed: {e}")
        logger.debug("[Schema validator cache] MISS — compiling validator")
        result = fetch_validator()
        if not replay_mode:
            try:
                schema_hash = self._compute_schema_hash(schema)
                cache_key = f"schema_validator:{schema_hash}"
                self._cache.set_json(cache_key, result, ttl_seconds=self._ttl)
            except ValueError:
                pass
            # guardian: allow-silent-swallow
            except Exception as e:
                logger.warning(f"[Schema validator cache] Cache write failed: {e}")
        return result

    def _compute_schema_hash(self, schema: dict[str, Any]) -> str:
        """Compute deterministic hash of schema for cache key."""
        schema_json = json.dumps(schema, sort_keys=True)
        schema_hash = hashlib.sha256(schema_json.encode("utf-8")).hexdigest()
        _require_hash_segment("schema_hash", schema_hash)
        return schema_hash

    def invalidate(self, schema: dict[str, Any]) -> None:
        """Invalidate cached validator for specific schema.

        Note: This is a no-op since cache keys are content-addressed.
        Schema changes automatically invalidate via different hash.
        """
        logger.debug("[Schema validator cache] invalidate called (no-op for content-addressed cache)")


def get_schema_validator_cache() -> SchemaValidatorCache:
    """Get the singleton schema validator cache instance."""
    return SchemaValidatorCache()
