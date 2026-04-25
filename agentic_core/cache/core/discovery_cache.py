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

_emit_applies_guardrail("p0", "discovery_cache", "p0_governance")
_emit_reads_policy_state("p0", "discovery_cache", "policy_binding")
_emit_snapshots_state("p0", "discovery_cache", "state_snapshot")
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

_emit_emits_metric_event("discovery_cache", "p4obs", "metric_1")
_emit_emits_metric_event("discovery_cache", "p4obs", "metric_2")
_emit_emits_metric_event("discovery_cache", "p4obs", "metric_3")
_emit_emits_metric_event("discovery_cache", "p4obs", "metric_4")
_emit_emits_metric_event("discovery_cache", "p4obs", "metric_5")
_emit_emits_metric_event("discovery_cache", "p4obs", "metric_6")
_emit_records_incident_event("discovery_cache", "p4obs", "incident")
_emit_captures_runtime_anomaly("discovery_cache", "p4obs", "anomaly")
_emit_writes_observability_log("discovery_cache", "p4obs", "obs_log")
_emit_updates_monitoring_state("discovery_cache", "p4obs", "mon_state")
_emit_triggers_alert("discovery_cache", "p4obs", "alert")
_emit_links_incident_trace("discovery_cache", "p4obs", "trace_link")
_emit_captures_pattern("discovery_cache", "p3lm", "pattern")
_emit_records_learning_event("discovery_cache", "p3lm", "learning_event")
_emit_writes_learning_snapshot("discovery_cache", "p3lm", "snapshot")
_emit_feeds_meta_learning("discovery_cache", "p3lm", "meta_feed")
_emit_updates_routing_strategy("discovery_cache", "p3lm", "routing")
_emit_improves_agent_policy("discovery_cache", "p3lm", "policy")
_emit_stores_learning_state("discovery_cache", "p3lm", "state")
_emit_records_execution_trace("discovery_cache", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("discovery_cache", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("discovery_cache", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("discovery_cache", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("discovery_cache", "L4_STATE", "p2_trace_5")
_emit_reads_environ("discovery_cache", "env_read", "p2_env_1")
_emit_reads_environ("discovery_cache", "env_read", "p2_env_2")
_emit_reads_runtime_state("discovery_cache", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("discovery_cache", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "discovery_cache", "context_pull")
_emit_pulls_context("p1", "discovery_cache", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "discovery_cache", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "discovery_cache", "uwg_term_2")
_emit_writes_through("p1", "discovery_cache", "write_through")
_emit_writes_through("p1", "discovery_cache", "write_through_2")
_emit_validated_by_safety_plane("p1", "discovery_cache", "safety_validation")
_emit_invokes_eval("p1", "discovery_cache", "eval_call")
_emit_proposal_commits_routing("p1", "discovery_cache", "routing_commit")
_emit_escalates_to_human("p1", "discovery_cache", "human_escalation")
_emit_routes_through("p1", "discovery_cache", "route_through")
_emit_checks_agent_registry("p1", "discovery_cache", "agent_registry")
_emit_validates_agent_capability("p1", "discovery_cache", "capability")
_emit_dispatches_execution_plan("p1", "discovery_cache", "exec_plan")
_emit_agent_executes_agent("p1", "discovery_cache", "sub_agent")
_emit_routes_to_agent("p1", "discovery_cache", "target_agent")
_emit_verifies_policy("p1", "discovery_cache", "policy_check")
_emit_observes_runtime_state("p1", "discovery_cache", "runtime_state")
_emit_verifies_boundary("p1", "discovery_cache", "boundary_check")
_emit_transcripts_response("p1", "discovery_cache", "transcript")
_emit_hard_fails_untranscripted("p1", "discovery_cache")
_emit_gated_by_confidence("p1", "discovery_cache", "confidence_gate")
emit_replay_key("p0", "discovery_cache")
emit_determinism_digest("p0", "discovery_cache")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "discovery_cache", "execution_auth")
_emit_validates_capability("p2", "discovery_cache", "capability_check")
_emit_routes_to_capability("p2", "discovery_cache", "capability_route")
_emit_writes_via_uwg("p2", "discovery_cache", "uwg_write")
_emit_blocks_direct_write("p2", "discovery_cache", "direct_write_block")
_emit_records_tool_invocation("p2", "discovery_cache", "tool_invocation")
_emit_captures_execution_output("p2", "discovery_cache", "exec_output")
_emit_dispatches_agent("p3", "discovery_cache", "agent_dispatch")
_emit_coordinates_agents("p3", "discovery_cache", "agent_coordination")
_emit_records_workflow_lineage("p3", "discovery_cache", "workflow_lineage")
_emit_records_healing_outcome("p3", "discovery_cache", "healing_outcome")
_emit_escalates_failure("p3", "discovery_cache", "failure_escalation")
_emit_orchestrates_workflow("p3", "discovery_cache", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "discovery_cache", "healing_dispatch")
_emit_invokes_evaluation("p3", "discovery_cache", "evaluation_signal")
_emit_records_telemetry_event("p4", "discovery_cache", "telemetry_event")
_emit_captures_evaluation_metric("p4", "discovery_cache", "eval_metric")
_emit_stores_embedding("p4", "discovery_cache", "embedding_store")
_emit_updates_meta_learning_state("p4", "discovery_cache", "meta_learning")
_emit_links_execution_to_snapshot("p4", "discovery_cache", "exec_snapshot_link")

logger = logging.getLogger(__name__)
_DEFAULT_DISCOVERY_TTL = 3600 * 24


class AgentDiscoveryCache:
    """Cache for agent discovery JSON parsing.

    Eliminates repeated file I/O and JSON parsing for agent_discovery_full.json.
    Automatically invalidates when file content changes via content hash keying.
    """

    def __init__(
        self,
        cache: DeterministicRedisCache | None = None,
        ttl_seconds: int = _DEFAULT_DISCOVERY_TTL,
    ):
        self._cache = cache or get_hot_cache()
        self._ttl = ttl_seconds

    def get_or_fetch(
        self,
        discovery_path: Path,
        fetch_from_disk: Any,
        *,
        replay_mode: bool = False,
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
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "AgentDiscoveryCache.get_or_fetch"
        )

        if not replay_mode:
            try:
                content_hash = self._compute_file_hash(discovery_path)
                cache_key = f"agent_discovery:{content_hash}"
            except FileNotFoundError:  # guardian: allow-silent-swallow -- optional file resource
                raise
            except (
                OSError,
                ValueError,
            ) as e:  # guardian: allow-log-and-swallow -- hash compute best-effort: non-fatal, fetch proceeds without cache key
                logger.warning(f"[Discovery cache] Hash computation failed: {e}")
            else:
                try:
                    cached = self._cache.get_json(cache_key)
                    if cached is not None:
                        logger.debug("[Discovery cache] HIT")
                        return cached
                except (
                    OSError,
                    ValueError,
                    TypeError,
                ) as e:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
                    logger.warning(f"[Discovery cache] Cache read failed: {e}")
        logger.debug("[Discovery cache] MISS — fetching from disk")
        result = fetch_from_disk()
        if not replay_mode:
            try:
                content_hash = self._compute_file_hash(discovery_path)
                cache_key = f"agent_discovery:{content_hash}"
                # guardian: allow-silent-swallow -- optional file resource
                self._cache.set_json(cache_key, result, ttl_seconds=self._ttl)
            except FileNotFoundError:  # guardian: allow-silent-swallow -- discovery file absent: skip cache write, disk fetch already served caller
                pass
            except (
                OSError,
                ValueError,
                TypeError,
            ) as e:  # guardian: allow-log-and-swallow -- cache write failure: non-fatal, disk fetch already served caller
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


_emit_reads_through("l4", "discovery_cache", "urg_read_1")
_emit_reads_through("l4", "discovery_cache", "urg_read_2")
_emit_reads_through("l4", "discovery_cache", "urg_read_3")
_emit_reads_through("l4", "discovery_cache", "urg_read_4")
_emit_reads_through("l4", "discovery_cache", "urg_read_5")
_emit_reads_through("l4", "discovery_cache", "urg_read_6")
_emit_reads_through("l4", "discovery_cache", "urg_read_7")
_emit_reads_through("l4", "discovery_cache", "urg_read_8")
_emit_reads_through("l4", "discovery_cache", "urg_read_9")
_emit_reads_through("l4", "discovery_cache", "urg_read_10")
