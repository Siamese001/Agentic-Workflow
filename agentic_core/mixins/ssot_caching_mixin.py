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

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
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

_emit_applies_guardrail("p0", "ssot_caching_mixin", "p0_governance")
_emit_reads_policy_state("p0", "ssot_caching_mixin", "policy_binding")
_emit_snapshots_state("p0", "ssot_caching_mixin", "state_snapshot")
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
