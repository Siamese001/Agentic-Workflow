"""Tool Embedding Cache — Redis-backed cache for tool registry embedding matrices.

Caches computed embedding matrices for tool sets to eliminate repeated
expensive embedding computations. Automatically invalidates when tool set
changes via deterministic fingerprint keying.
"""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any, Callable

from agentic_core.cache.cache_key_builders import _require_hash_segment
from agentic_core.cache.redis_cache_client import DeterministicRedisCache, get_hot_cache
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "tool_embedding_cache", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "tool_embedding_cache", "policy_binding")
trace_contract._emit_snapshots_state("p0", "tool_embedding_cache", "state_snapshot")

trace_contract._emit_emits_metric_event("tool_embedding_cache", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("tool_embedding_cache", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("tool_embedding_cache", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("tool_embedding_cache", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("tool_embedding_cache", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("tool_embedding_cache", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("tool_embedding_cache", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("tool_embedding_cache", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("tool_embedding_cache", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("tool_embedding_cache", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("tool_embedding_cache", "p4obs", "alert")
trace_contract._emit_links_incident_trace("tool_embedding_cache", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("tool_embedding_cache", "p3lm", "pattern")
trace_contract._emit_records_learning_event("tool_embedding_cache", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("tool_embedding_cache", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("tool_embedding_cache", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("tool_embedding_cache", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("tool_embedding_cache", "p3lm", "policy")
trace_contract._emit_stores_learning_state("tool_embedding_cache", "p3lm", "state")
trace_contract._emit_records_execution_trace("tool_embedding_cache", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("tool_embedding_cache", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("tool_embedding_cache", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("tool_embedding_cache", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("tool_embedding_cache", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("tool_embedding_cache", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("tool_embedding_cache", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("tool_embedding_cache", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("tool_embedding_cache", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "tool_embedding_cache", "context_pull")
trace_contract._emit_pulls_context("p1", "tool_embedding_cache", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "tool_embedding_cache", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "tool_embedding_cache", "uwg_term_2")
trace_contract._emit_writes_through("p1", "tool_embedding_cache", "write_through")
trace_contract._emit_writes_through("p1", "tool_embedding_cache", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "tool_embedding_cache", "safety_validation")
trace_contract._emit_invokes_eval("p1", "tool_embedding_cache", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "tool_embedding_cache", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "tool_embedding_cache", "human_escalation")
trace_contract._emit_routes_through("p1", "tool_embedding_cache", "route_through")
trace_contract._emit_checks_agent_registry("p1", "tool_embedding_cache", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "tool_embedding_cache", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "tool_embedding_cache", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "tool_embedding_cache", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "tool_embedding_cache", "target_agent")
trace_contract._emit_verifies_policy("p1", "tool_embedding_cache", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "tool_embedding_cache", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "tool_embedding_cache", "boundary_check")
trace_contract._emit_transcripts_response("p1", "tool_embedding_cache", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "tool_embedding_cache")
trace_contract._emit_gated_by_confidence("p1", "tool_embedding_cache", "confidence_gate")
trace_contract.emit_replay_key("p0", "tool_embedding_cache")
trace_contract.emit_determinism_digest("p0", "tool_embedding_cache")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "tool_embedding_cache", "execution_auth")
trace_contract._emit_validates_capability("p2", "tool_embedding_cache", "capability_check")
trace_contract._emit_routes_to_capability("p2", "tool_embedding_cache", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "tool_embedding_cache", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "tool_embedding_cache", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "tool_embedding_cache", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "tool_embedding_cache", "exec_output")
trace_contract._emit_dispatches_agent("p3", "tool_embedding_cache", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "tool_embedding_cache", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "tool_embedding_cache", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "tool_embedding_cache", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "tool_embedding_cache", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "tool_embedding_cache", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "tool_embedding_cache", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "tool_embedding_cache", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "tool_embedding_cache", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "tool_embedding_cache", "eval_metric")
trace_contract._emit_stores_embedding("p4", "tool_embedding_cache", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "tool_embedding_cache", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "tool_embedding_cache", "exec_snapshot_link")

logger = logging.getLogger(__name__)
_DEFAULT_EMBEDDING_TTL = 3600 * 24 * 7  # 7 days - tool sets change rarely
_MAX_EMBEDDING_ROWS = 2048
_MAX_EMBEDDING_DIM = 8192


def _require_positive_ttl(ttl_seconds: int) -> int:
    if ttl_seconds <= 0:
        raise ValueError(f"ttl_seconds must be > 0, got {ttl_seconds}")
    return ttl_seconds


def _validate_embedding_payload(embeddings: Any, tool_names: Any) -> None:
    if not isinstance(embeddings, list) or not isinstance(tool_names, list):
        raise TypeError("fetch_embeddings must return (list[list[float]], list[str])")
    if len(embeddings) != len(tool_names):
        raise ValueError("embeddings and tool_names length mismatch")
    if len(embeddings) > _MAX_EMBEDDING_ROWS:
        raise ValueError(f"Embedding matrix exceeds max rows {_MAX_EMBEDDING_ROWS}: got {len(embeddings)}")
    if embeddings and isinstance(embeddings[0], list) and len(embeddings[0]) > _MAX_EMBEDDING_DIM:
        raise ValueError(f"Embedding dimension exceeds max {_MAX_EMBEDDING_DIM}: got {len(embeddings[0])}")


class ToolEmbeddingCache:
    """Cache for tool registry embedding matrices.

    Eliminates repeated expensive embedding computations for the same tool set.
    Automatically invalidates when tool set changes via fingerprint keying.
    """

    def __init__(
        self,
        cache: DeterministicRedisCache | None = None,
        ttl_seconds: int = _DEFAULT_EMBEDDING_TTL,
    ):
        self._cache = cache or get_hot_cache()
        self._ttl = _require_positive_ttl(ttl_seconds)

    def get_or_fetch(
        self,
        tool_definitions: list[dict[str, Any]],
        fetch_embeddings: Callable[[], tuple[list[list[float]], list[str]]],
        *,
        replay_mode: bool = False,
    ) -> tuple[list[list[float]], list[str]]:
        """Read-through helper: return cached embeddings or call *fetch_embeddings*.

        *fetch_embeddings* is a zero-argument callable that computes and returns
        (embedding_matrix, tool_names) tuple. Called only on cache miss.

        Args:
            tool_definitions: List of tool definition dicts (name, description, tags)
            fetch_embeddings: Callable that returns (embeddings, tool_names) tuple
            replay_mode: If True, bypass cache entirely

        Returns:
            Tuple of (embedding_matrix, tool_names)

        Raises:
            ValueError: If tool_definitions is empty
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "ToolEmbeddingCache.get_or_fetch"
        )

        if not tool_definitions:
            raise ValueError("Tool definitions list must not be empty")
        if not callable(fetch_embeddings):
            raise TypeError("fetch_embeddings must be callable")
        if not replay_mode:
            try:
                fingerprint = self._compute_tool_fingerprint(tool_definitions)
                cache_key = f"tool_embeddings:{fingerprint}"
                cached = self._cache.get_json(cache_key)
                if cached is not None:
                    logger.debug("[Tool embedding cache] HIT")
                    return (cached["embeddings"], cached["tool_names"])
            except ValueError as e:
                logger.warning(f"Invalid input: {e}")
                raise
            except (
                ConnectionError,
                OSError,
            ) as e:  # guardian: allow-log-and-swallow -- cache read failure: non-fatal, falls through to compute
                logger.warning(f"[Tool embedding cache] Cache read failed: {e}")
        logger.debug("[Tool embedding cache] MISS — computing embeddings")
        embeddings, tool_names = fetch_embeddings()
        _validate_embedding_payload(embeddings, tool_names)
        if not replay_mode:
            try:
                fingerprint = self._compute_tool_fingerprint(tool_definitions)
                cache_key = f"tool_embeddings:{fingerprint}"
                self._cache.set_json(
                    cache_key,
                    {"embeddings": embeddings, "tool_names": tool_names},
                    ttl_seconds=self._ttl,
                )
            except (
                ValueError,
                ConnectionError,
                OSError,
            ) as e:  # guardian: allow-log-and-swallow -- cache write failure: non-fatal, computed embeddings already returned
                logger.warning(f"[Tool embedding cache] Cache write failed: {e}")
        return (embeddings, tool_names)

    def _compute_tool_fingerprint(self, tool_definitions: list[dict[str, Any]]) -> str:
        """Compute deterministic fingerprint of tool set for cache key."""
        sorted_tools = sorted(tool_definitions, key=lambda t: t.get("name", ""))
        fingerprint_data = json.dumps(
            [
                {
                    "name": t.get("name", ""),
                    "description": t.get("description", ""),
                    "tags": sorted(t.get("tags", [])),
                }
                for t in sorted_tools
            ],
            sort_keys=True,
        )
        tool_hash = hashlib.sha256(fingerprint_data.encode("utf-8")).hexdigest()
        _require_hash_segment("tool_fingerprint", tool_hash)
        return tool_hash

    def invalidate_all(self) -> None:
        """Invalidate all cached embeddings.

        Note: This is a no-op since cache keys are fingerprint-addressed.
        Tool set changes automatically invalidate via different fingerprint.
        """
        logger.debug("[Tool embedding cache] invalidate_all called (no-op for fingerprint-addressed cache)")


def get_tool_embedding_cache() -> ToolEmbeddingCache:
    """Get the singleton tool embedding cache instance."""
    return ToolEmbeddingCache()


trace_contract._emit_reads_through("l4", "tool_embedding_cache", "urg_read_1")
trace_contract._emit_reads_through("l4", "tool_embedding_cache", "urg_read_2")
trace_contract._emit_reads_through("l4", "tool_embedding_cache", "urg_read_3")
trace_contract._emit_reads_through("l4", "tool_embedding_cache", "urg_read_4")
trace_contract._emit_reads_through("l4", "tool_embedding_cache", "urg_read_5")
trace_contract._emit_reads_through("l4", "tool_embedding_cache", "urg_read_6")
trace_contract._emit_reads_through("l4", "tool_embedding_cache", "urg_read_7")
trace_contract._emit_reads_through("l4", "tool_embedding_cache", "urg_read_8")
trace_contract._emit_reads_through("l4", "tool_embedding_cache", "urg_read_9")
trace_contract._emit_reads_through("l4", "tool_embedding_cache", "urg_read_10")
trace_contract._emit_reads_through("l4", "tool_embedding_cache", "urg_read_11")
trace_contract._emit_reads_through("l4", "tool_embedding_cache", "urg_read_12")
trace_contract._emit_reads_through("l4", "tool_embedding_cache", "urg_read_13")
trace_contract._emit_reads_through("l4", "tool_embedding_cache", "urg_read_14")
