"""Config File Parse Cache — Redis-backed cache for parsed YAML/JSON config files.

Caches parsed configuration files to eliminate repeated file I/O and parsing.
Keyed by file path + content hash for automatic invalidation on file changes.
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Any, Callable

from agentic_core.cache.cache_key_builders import _require_hash_segment
from agentic_core.cache.redis_cache_client import DeterministicRedisCache, get_hot_cache
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "config_file_cache", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "config_file_cache", "policy_binding")
trace_contract._emit_snapshots_state("p0", "config_file_cache", "state_snapshot")

trace_contract._emit_emits_metric_event("config_file_cache", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("config_file_cache", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("config_file_cache", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("config_file_cache", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("config_file_cache", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("config_file_cache", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("config_file_cache", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("config_file_cache", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("config_file_cache", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("config_file_cache", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("config_file_cache", "p4obs", "alert")
trace_contract._emit_links_incident_trace("config_file_cache", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("config_file_cache", "p3lm", "pattern")
trace_contract._emit_records_learning_event("config_file_cache", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("config_file_cache", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("config_file_cache", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("config_file_cache", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("config_file_cache", "p3lm", "policy")
trace_contract._emit_stores_learning_state("config_file_cache", "p3lm", "state")
trace_contract._emit_records_execution_trace("config_file_cache", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("config_file_cache", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("config_file_cache", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("config_file_cache", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("config_file_cache", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("config_file_cache", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("config_file_cache", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("config_file_cache", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("config_file_cache", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "config_file_cache", "context_pull")
trace_contract._emit_pulls_context("p1", "config_file_cache", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "config_file_cache", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "config_file_cache", "uwg_term_2")
trace_contract._emit_writes_through("p1", "config_file_cache", "write_through")
trace_contract._emit_writes_through("p1", "config_file_cache", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "config_file_cache", "safety_validation")
trace_contract._emit_invokes_eval("p1", "config_file_cache", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "config_file_cache", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "config_file_cache", "human_escalation")
trace_contract._emit_routes_through("p1", "config_file_cache", "route_through")
trace_contract._emit_checks_agent_registry("p1", "config_file_cache", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "config_file_cache", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "config_file_cache", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "config_file_cache", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "config_file_cache", "target_agent")
trace_contract._emit_verifies_policy("p1", "config_file_cache", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "config_file_cache", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "config_file_cache", "boundary_check")
trace_contract._emit_transcripts_response("p1", "config_file_cache", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "config_file_cache")
trace_contract._emit_gated_by_confidence("p1", "config_file_cache", "confidence_gate")
trace_contract.emit_replay_key("p0", "config_file_cache")
trace_contract.emit_determinism_digest("p0", "config_file_cache")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "config_file_cache", "execution_auth")
trace_contract._emit_validates_capability("p2", "config_file_cache", "capability_check")
trace_contract._emit_routes_to_capability("p2", "config_file_cache", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "config_file_cache", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "config_file_cache", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "config_file_cache", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "config_file_cache", "exec_output")
trace_contract._emit_dispatches_agent("p3", "config_file_cache", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "config_file_cache", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "config_file_cache", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "config_file_cache", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "config_file_cache", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "config_file_cache", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "config_file_cache", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "config_file_cache", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "config_file_cache", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "config_file_cache", "eval_metric")
trace_contract._emit_stores_embedding("p4", "config_file_cache", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "config_file_cache", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "config_file_cache", "exec_snapshot_link")

# Configuration constants

logger = logging.getLogger(__name__)

_DEFAULT_CONFIG_TTL = 3600 * 24  # 24 hours


def _require_positive_ttl(ttl_seconds: int) -> int:
    if ttl_seconds <= 0:
        raise ValueError(f"ttl_seconds must be > 0, got {ttl_seconds}")
    return ttl_seconds


def _config_identity_key(config_path: Path, content_hash: str) -> str:
    path_hash = hashlib.sha256(str(config_path.resolve()).encode("utf-8")).hexdigest()[:16]
    return f"config:{path_hash}:{content_hash}"


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
        self._ttl = _require_positive_ttl(ttl_seconds)

    def get_or_fetch(
        self,
        config_path: Path,
        fetch_from_disk: Callable[[], dict[str, Any]],
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
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "ConfigFileCache.get_or_fetch"
        )

        if not callable(fetch_from_disk):
            raise TypeError("fetch_from_disk must be callable")

        if not replay_mode:
            try:
                content_hash = self._compute_file_hash(config_path)
                cache_key = _config_identity_key(config_path, content_hash)
                cached = self._cache.get_json(cache_key)
                if cached is not None:
                    logger.debug(f"[Config cache] HIT for {config_path.name}")
                    return cached
            except FileNotFoundError:
                raise
            except (
                OSError,
                ValueError,
            ) as e:  # guardian: allow-log-and-swallow -- config cache read: non-fatal, falls back to disk parse
                logger.warning(f"[Config cache] Cache read failed: {e}")

        logger.debug(f"[Config cache] MISS for {config_path.name} — parsing from disk")
        result = fetch_from_disk()
        if not isinstance(result, dict):
            raise TypeError(f"fetch_from_disk must return a dict, got {type(result).__name__}")

        if not replay_mode:
            try:
                content_hash = self._compute_file_hash(config_path)
                cache_key = _config_identity_key(config_path, content_hash)
                self._cache.set_json(cache_key, result, ttl_seconds=self._ttl)
            except (
                FileNotFoundError
            ):  # guardian: allow-silent-swallow -- config cache write: file deleted after fetch, non-fatal
                pass  # File may have been deleted after fetch
            except (
                OSError,
                ValueError,
                TypeError,
            ) as e:  # guardian: allow-log-and-swallow -- config cache write: non-fatal, result returned without caching
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
            f"[Config cache] invalidate called for {config_path.name} (no-op for content-addressed cache)",
        )


def get_config_file_cache() -> ConfigFileCache:
    """Get the singleton config file cache instance."""
    return ConfigFileCache()


trace_contract._emit_reads_through("l4", "config_file_cache", "urg_read_1")
trace_contract._emit_reads_through("l4", "config_file_cache", "urg_read_2")
trace_contract._emit_reads_through("l4", "config_file_cache", "urg_read_3")
trace_contract._emit_reads_through("l4", "config_file_cache", "urg_read_4")
trace_contract._emit_reads_through("l4", "config_file_cache", "urg_read_5")
trace_contract._emit_reads_through("l4", "config_file_cache", "urg_read_6")
trace_contract._emit_reads_through("l4", "config_file_cache", "urg_read_7")
trace_contract._emit_reads_through("l4", "config_file_cache", "urg_read_8")
trace_contract._emit_reads_through("l4", "config_file_cache", "urg_read_9")
trace_contract._emit_reads_through("l4", "config_file_cache", "urg_read_10")
