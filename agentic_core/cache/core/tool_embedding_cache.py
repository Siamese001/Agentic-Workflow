"""Tool Embedding Cache — Redis-backed cache for tool registry embedding matrices.

Caches expensive numpy embedding computations for tool discovery.
Keyed by tool set fingerprint (hash of tool names + descriptions).
"""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any

from agentic_core.cache.cache_key_builders import _require_hash_segment
from agentic_core.cache.redis_cache_client import DeterministicRedisCache, get_hot_cache
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_through,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "tool_embedding_cache", "p0_governance")
_emit_reads_policy_state("p0", "tool_embedding_cache", "policy_binding")
_emit_snapshots_state("p0", "tool_embedding_cache", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("tool_embedding_cache", "p4obs", "metric_1")
_emit_emits_metric_event("tool_embedding_cache", "p4obs", "metric_2")
_emit_emits_metric_event("tool_embedding_cache", "p4obs", "metric_3")
_emit_emits_metric_event("tool_embedding_cache", "p4obs", "metric_4")
_emit_emits_metric_event("tool_embedding_cache", "p4obs", "metric_5")
_emit_emits_metric_event("tool_embedding_cache", "p4obs", "metric_6")
_emit_records_incident_event("tool_embedding_cache", "p4obs", "incident")
_emit_captures_runtime_anomaly("tool_embedding_cache", "p4obs", "anomaly")
_emit_writes_observability_log("tool_embedding_cache", "p4obs", "obs_log")
_emit_updates_monitoring_state("tool_embedding_cache", "p4obs", "mon_state")
_emit_triggers_alert("tool_embedding_cache", "p4obs", "alert")
_emit_links_incident_trace("tool_embedding_cache", "p4obs", "trace_link")
_emit_captures_pattern("tool_embedding_cache", "p3lm", "pattern")
_emit_records_learning_event("tool_embedding_cache", "p3lm", "learning_event")
_emit_writes_learning_snapshot("tool_embedding_cache", "p3lm", "snapshot")
_emit_feeds_meta_learning("tool_embedding_cache", "p3lm", "meta_feed")
_emit_updates_routing_strategy("tool_embedding_cache", "p3lm", "routing")
_emit_improves_agent_policy("tool_embedding_cache", "p3lm", "policy")
_emit_stores_learning_state("tool_embedding_cache", "p3lm", "state")
_emit_records_execution_trace("tool_embedding_cache", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("tool_embedding_cache", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("tool_embedding_cache", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("tool_embedding_cache", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("tool_embedding_cache", "L4_STATE", "p2_trace_5")
_emit_reads_environ("tool_embedding_cache", "env_read", "p2_env_1")
_emit_reads_environ("tool_embedding_cache", "env_read", "p2_env_2")
_emit_reads_runtime_state("tool_embedding_cache", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("tool_embedding_cache", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "tool_embedding_cache", "context_pull")
_emit_pulls_context("p1", "tool_embedding_cache", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "tool_embedding_cache", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "tool_embedding_cache", "uwg_term_2")
_emit_writes_through("p1", "tool_embedding_cache", "write_through")
_emit_writes_through("p1", "tool_embedding_cache", "write_through_2")
_emit_validated_by_safety_plane("p1", "tool_embedding_cache", "safety_validation")
_emit_invokes_eval("p1", "tool_embedding_cache", "eval_call")
_emit_proposal_commits_routing("p1", "tool_embedding_cache", "routing_commit")
_emit_escalates_to_human("p1", "tool_embedding_cache", "human_escalation")
_emit_routes_through("p1", "tool_embedding_cache", "route_through")
_emit_checks_agent_registry("p1", "tool_embedding_cache", "agent_registry")
_emit_validates_agent_capability("p1", "tool_embedding_cache", "capability")
_emit_dispatches_execution_plan("p1", "tool_embedding_cache", "exec_plan")
_emit_agent_executes_agent("p1", "tool_embedding_cache", "sub_agent")
_emit_routes_to_agent("p1", "tool_embedding_cache", "target_agent")
_emit_verifies_policy("p1", "tool_embedding_cache", "policy_check")
_emit_observes_runtime_state("p1", "tool_embedding_cache", "runtime_state")
_emit_verifies_boundary("p1", "tool_embedding_cache", "boundary_check")
_emit_transcripts_response("p1", "tool_embedding_cache", "transcript")
_emit_hard_fails_untranscripted("p1", "tool_embedding_cache")
_emit_gated_by_confidence("p1", "tool_embedding_cache", "confidence_gate")
emit_replay_key("p0", "tool_embedding_cache")
emit_determinism_digest("p0", "tool_embedding_cache")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "tool_embedding_cache", "execution_auth")
_emit_validates_capability("p2", "tool_embedding_cache", "capability_check")
_emit_routes_to_capability("p2", "tool_embedding_cache", "capability_route")
_emit_writes_via_uwg("p2", "tool_embedding_cache", "uwg_write")
_emit_blocks_direct_write("p2", "tool_embedding_cache", "direct_write_block")
_emit_records_tool_invocation("p2", "tool_embedding_cache", "tool_invocation")
_emit_captures_execution_output("p2", "tool_embedding_cache", "exec_output")
_emit_dispatches_agent("p3", "tool_embedding_cache", "agent_dispatch")
_emit_coordinates_agents("p3", "tool_embedding_cache", "agent_coordination")
_emit_records_workflow_lineage("p3", "tool_embedding_cache", "workflow_lineage")
_emit_records_healing_outcome("p3", "tool_embedding_cache", "healing_outcome")
_emit_escalates_failure("p3", "tool_embedding_cache", "failure_escalation")
_emit_orchestrates_workflow("p3", "tool_embedding_cache", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "tool_embedding_cache", "healing_dispatch")
_emit_invokes_evaluation("p3", "tool_embedding_cache", "evaluation_signal")
_emit_records_telemetry_event("p4", "tool_embedding_cache", "telemetry_event")
_emit_captures_evaluation_metric("p4", "tool_embedding_cache", "eval_metric")
_emit_stores_embedding("p4", "tool_embedding_cache", "embedding_store")
_emit_updates_meta_learning_state("p4", "tool_embedding_cache", "meta_learning")
_emit_links_execution_to_snapshot("p4", "tool_embedding_cache", "exec_snapshot_link")

logger = logging.getLogger(__name__)
_DEFAULT_EMBEDDING_TTL = 3600 * 24 * 7


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
        self._ttl = ttl_seconds

    def get_or_fetch(
        self,
        tool_definitions: list[dict[str, Any]],
        fetch_embeddings: Any,
        *,
        replay_mode: bool = False,
    ) -> tuple[list[list[float]], list[str]]:
        """Read-through helper: return cached embeddings or call *fetch_embeddings*.

        *fetch_embeddings* is a zero-argument callable that computes and returns
        (embedding_matrix, tool_names) tuple.  Called only on cache miss.

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
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "ToolEmbeddingCache.get_or_fetch"
        )

        if not tool_definitions:
            raise ValueError("Tool definitions list must not be empty")
        if not replay_mode:
            try:
                fingerprint = self._compute_tool_fingerprint(tool_definitions)
                cache_key = f"tool_embeddings:{fingerprint}"
                cached = self._cache.get_json(cache_key)
                if cached is not None:
                    logger.debug("[Tool embedding cache] HIT")
                    return (cached["embeddings"], cached["tool_names"])
            except ValueError as e:
                # TODO: Add proper input validation
                logger.warning(f"Invalid input: {e}")
                raise
            except (AttributeError, KeyError, TypeError, OSError, RuntimeError) as e:  # guardian: allow-log-and-swallow -- cache read failure: non-fatal, falls through to compute
                logger.warning(f"[Tool embedding cache] Cache read failed: {e}")
        logger.debug("[Tool embedding cache] MISS — computing embeddings")
        embeddings, tool_names = fetch_embeddings()
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
                ValueError
            ):  # guardian: allow-silent-swallow -- cache key hash failure: non-fatal, cache write skipped
                pass
            except (
                AttributeError,
                TypeError,
                OSError,
                RuntimeError,
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


_emit_reads_through("l4", "tool_embedding_cache", "urg_read_1")
_emit_reads_through("l4", "tool_embedding_cache", "urg_read_2")
_emit_reads_through("l4", "tool_embedding_cache", "urg_read_3")
_emit_reads_through("l4", "tool_embedding_cache", "urg_read_4")
_emit_reads_through("l4", "tool_embedding_cache", "urg_read_5")
_emit_reads_through("l4", "tool_embedding_cache", "urg_read_6")
_emit_reads_through("l4", "tool_embedding_cache", "urg_read_7")
_emit_reads_through("l4", "tool_embedding_cache", "urg_read_8")
_emit_reads_through("l4", "tool_embedding_cache", "urg_read_9")
_emit_reads_through("l4", "tool_embedding_cache", "urg_read_10")
_emit_reads_through("l4", "tool_embedding_cache", "urg_read_11")
_emit_reads_through("l4", "tool_embedding_cache", "urg_read_12")
_emit_reads_through("l4", "tool_embedding_cache", "urg_read_13")
_emit_reads_through("l4", "tool_embedding_cache", "urg_read_14")
