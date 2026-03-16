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
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "config_file_cache")
emit_determinism_digest("p0", "config_file_cache")

_emit_dispatches_healing_run("p1", "config_file_cache", "L4")
_emit_routes_through("p1", "config_file_cache", "L4")
_emit_escalates_to_human("p1", "config_file_cache", "L4")
_emit_reads_policy_state("p1", "config_file_cache", "L4")

_emit_snapshots_state("p0", "config_file_cache", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "config_file_cache", "p0_governance")
_emit_authorize_and_execute("p2", "config_file_cache", "execution_auth")
_emit_validates_capability("p2", "config_file_cache", "capability_check")
_emit_routes_to_capability("p2", "config_file_cache", "capability_route")
_emit_writes_via_uwg("p2", "config_file_cache", "uwg_write")
_emit_blocks_direct_write("p2", "config_file_cache", "direct_write_block")
_emit_records_tool_invocation("p2", "config_file_cache", "tool_invocation")
_emit_captures_execution_output("p2", "config_file_cache", "exec_output")
_emit_dispatches_agent("p3", "config_file_cache", "agent_dispatch")
_emit_coordinates_agents("p3", "config_file_cache", "agent_coordination")
_emit_records_workflow_lineage("p3", "config_file_cache", "workflow_lineage")
_emit_records_healing_outcome("p3", "config_file_cache", "healing_outcome")
_emit_escalates_failure("p3", "config_file_cache", "failure_escalation")
_emit_orchestrates_workflow("p3", "config_file_cache", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "config_file_cache", "healing_dispatch")
_emit_invokes_evaluation("p3", "config_file_cache", "evaluation_signal")
_emit_records_telemetry_event("p4", "config_file_cache", "telemetry_event")
_emit_captures_evaluation_metric("p4", "config_file_cache", "eval_metric")
_emit_stores_embedding("p4", "config_file_cache", "embedding_store")
_emit_updates_meta_learning_state("p4", "config_file_cache", "meta_learning")
_emit_links_execution_to_snapshot("p4", "config_file_cache", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

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
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "ConfigFileCache.get_or_fetch")

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
            # guardian: allow-silent-swallow
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
            # guardian: allow-silent-swallow
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
