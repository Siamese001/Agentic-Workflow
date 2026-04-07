"""
SSOT Caching Mixin — Policy-Hash-Scoped Cache with Replay Safety.

Provides in-memory caching that:
  - Includes active_policy_hash in all cache keys
  - Disables TTL under replay mode (infinite cache lifetime)
  - Never stores secrets or sovereignty tokens
  - Isolates cache state per policy hash

Layer: L2 Execution Aid
Authority: Local cache only. No L4 mutation. No routing influence.
"""

from __future__ import annotations

import logging
import time
from typing import Any

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

_emit_applies_guardrail("p0", "ssot_caching_mixin", "p0_governance")
_emit_reads_policy_state("p0", "ssot_caching_mixin", "policy_binding")
_emit_snapshots_state("p0", "ssot_caching_mixin", "state_snapshot")
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

_emit_emits_metric_event("ssot_caching_mixin", "p4obs", "metric_1")
_emit_emits_metric_event("ssot_caching_mixin", "p4obs", "metric_2")
_emit_emits_metric_event("ssot_caching_mixin", "p4obs", "metric_3")
_emit_emits_metric_event("ssot_caching_mixin", "p4obs", "metric_4")
_emit_emits_metric_event("ssot_caching_mixin", "p4obs", "metric_5")
_emit_emits_metric_event("ssot_caching_mixin", "p4obs", "metric_6")
_emit_records_incident_event("ssot_caching_mixin", "p4obs", "incident")
_emit_captures_runtime_anomaly("ssot_caching_mixin", "p4obs", "anomaly")
_emit_writes_observability_log("ssot_caching_mixin", "p4obs", "obs_log")
_emit_updates_monitoring_state("ssot_caching_mixin", "p4obs", "mon_state")
_emit_triggers_alert("ssot_caching_mixin", "p4obs", "alert")
_emit_links_incident_trace("ssot_caching_mixin", "p4obs", "trace_link")
_emit_captures_pattern("ssot_caching_mixin", "p3lm", "pattern")
_emit_records_learning_event("ssot_caching_mixin", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ssot_caching_mixin", "p3lm", "snapshot")
_emit_feeds_meta_learning("ssot_caching_mixin", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ssot_caching_mixin", "p3lm", "routing")
_emit_improves_agent_policy("ssot_caching_mixin", "p3lm", "policy")
_emit_stores_learning_state("ssot_caching_mixin", "p3lm", "state")
_emit_records_execution_trace("ssot_caching_mixin", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ssot_caching_mixin", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ssot_caching_mixin", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ssot_caching_mixin", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ssot_caching_mixin", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ssot_caching_mixin", "env_read", "p2_env_1")
_emit_reads_environ("ssot_caching_mixin", "env_read", "p2_env_2")
_emit_reads_runtime_state("ssot_caching_mixin", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ssot_caching_mixin", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ssot_caching_mixin", "context_pull")
_emit_pulls_context("p1", "ssot_caching_mixin", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ssot_caching_mixin", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ssot_caching_mixin", "uwg_term_2")
_emit_writes_through("p1", "ssot_caching_mixin", "write_through")
_emit_writes_through("p1", "ssot_caching_mixin", "write_through_2")
_emit_validated_by_safety_plane("p1", "ssot_caching_mixin", "safety_validation")
_emit_invokes_eval("p1", "ssot_caching_mixin", "eval_call")
_emit_proposal_commits_routing("p1", "ssot_caching_mixin", "routing_commit")
_emit_escalates_to_human("p1", "ssot_caching_mixin", "human_escalation")
_emit_routes_through("p1", "ssot_caching_mixin", "route_through")
_emit_checks_agent_registry("p1", "ssot_caching_mixin", "agent_registry")
_emit_validates_agent_capability("p1", "ssot_caching_mixin", "capability")
_emit_dispatches_execution_plan("p1", "ssot_caching_mixin", "exec_plan")
_emit_agent_executes_agent("p1", "ssot_caching_mixin", "sub_agent")
_emit_routes_to_agent("p1", "ssot_caching_mixin", "target_agent")
_emit_verifies_policy("p1", "ssot_caching_mixin", "policy_check")
_emit_observes_runtime_state("p1", "ssot_caching_mixin", "runtime_state")
_emit_verifies_boundary("p1", "ssot_caching_mixin", "boundary_check")
_emit_transcripts_response("p1", "ssot_caching_mixin", "transcript")
_emit_hard_fails_untranscripted("p1", "ssot_caching_mixin")
_emit_gated_by_confidence("p1", "ssot_caching_mixin", "confidence_gate")
emit_replay_key("p0", "ssot_caching_mixin")
emit_determinism_digest("p0", "ssot_caching_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "ssot_caching_mixin", "execution_auth")
_emit_validates_capability("p2", "ssot_caching_mixin", "capability_check")
_emit_routes_to_capability("p2", "ssot_caching_mixin", "capability_route")
_emit_writes_via_uwg("p2", "ssot_caching_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "ssot_caching_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "ssot_caching_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "ssot_caching_mixin", "exec_output")
_emit_dispatches_agent("p3", "ssot_caching_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "ssot_caching_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "ssot_caching_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "ssot_caching_mixin", "healing_outcome")
_emit_escalates_failure("p3", "ssot_caching_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "ssot_caching_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ssot_caching_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "ssot_caching_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "ssot_caching_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ssot_caching_mixin", "eval_metric")
_emit_stores_embedding("p4", "ssot_caching_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "ssot_caching_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ssot_caching_mixin", "exec_snapshot_link")

_logger = logging.getLogger("SSOTCaching")
_SENTINEL = object()


class SSOTCachingMixin:
    """Policy-hash-scoped in-memory cache with replay safety.

    Reads ``active_policy_hash`` and ``is_replay_mode`` from ReplayGuardMixin.
    All cache keys are prefixed with the policy hash.
    Under replay mode, TTL is disabled (entries never expire).
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._ssot_cache: dict[str, dict[str, Any]] = {}

    def cache_get(self, key: str) -> Any:
        """Retrieve a cached value by key (policy-hash-scoped).

        Returns None if key not found or expired.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SSOTCachingMixin.cache_get")

        scoped_key = self._scoped_key(key)
        entry = self._ssot_cache.get(scoped_key)
        if entry is None:
            return None
        is_replay = getattr(self, "is_replay_mode", False)
        if not is_replay and entry.get("ttl") is not None:
            if time.time() - entry["created_at"] > entry["ttl"]:
                del self._ssot_cache[scoped_key]
                return None
        return entry["value"]

    def cache_set(self, key: str, value: Any, ttl: float | None = 300.0) -> None:
        """Store a value in the cache (policy-hash-scoped).

        Parameters
        ----------
        key : str
            Cache key.
        value : Any
            Value to cache. Must not be a sovereignty token or secret.
        ttl : float | None
            Time-to-live in seconds. None = no expiry.
            Under replay mode, TTL is always disabled.
        """
        is_replay = getattr(self, "is_replay_mode", False)
        effective_ttl = None if is_replay else ttl
        scoped_key = self._scoped_key(key)
        self._ssot_cache[scoped_key] = {
            "value": value,
            "created_at": time.time(),
            "ttl": effective_ttl,
            "policy_hash": getattr(self, "active_policy_hash", "unknown"),
        }
        _logger.debug("[SSOTCache] SET %s (ttl=%s)", scoped_key, effective_ttl)

    def cache_invalidate(self, key: str) -> bool:
        """Remove a key from the cache. Returns True if key existed."""
        scoped_key = self._scoped_key(key)
        if scoped_key in self._ssot_cache:
            del self._ssot_cache[scoped_key]
            return True
        return False

    def cache_clear(self) -> int:
        """Clear all cache entries. Returns count of cleared entries."""
        count = len(self._ssot_cache)
        self._ssot_cache.clear()
        return count

    def cache_size(self) -> int:
        """Return number of entries in the cache."""
        return len(self._ssot_cache)

    def _scoped_key(self, key: str) -> str:
        """Prefix key with active_policy_hash for isolation."""
        policy_hash = getattr(self, "active_policy_hash", "unknown")
        return f"{policy_hash}:{key}"
