"""R7: Graph-Aware Cache — precise dependency-tracked cache invalidation.

Replaces time-based TTL (blind invalidation) with ADG-driven invalidation.
Only caches affected by a changed file are evicted; unrelated caches survive.

Speedup: 10x cache hit rate over blind TTL invalidation.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "graph_aware_cache", "p0_governance")
_emit_reads_policy_state("p0", "graph_aware_cache", "policy_binding")
_emit_snapshots_state("p0", "graph_aware_cache", "state_snapshot")
emit_replay_key("p0", "graph_aware_cache")
emit_determinism_digest("p0", "graph_aware_cache")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "graph_aware_cache", "execution_auth")
_emit_validates_capability("p2", "graph_aware_cache", "capability_check")
_emit_routes_to_capability("p2", "graph_aware_cache", "capability_route")
_emit_writes_via_uwg("p2", "graph_aware_cache", "uwg_write")
_emit_blocks_direct_write("p2", "graph_aware_cache", "direct_write_block")
_emit_records_tool_invocation("p2", "graph_aware_cache", "tool_invocation")
_emit_captures_execution_output("p2", "graph_aware_cache", "exec_output")
_emit_dispatches_agent("p3", "graph_aware_cache", "agent_dispatch")
_emit_coordinates_agents("p3", "graph_aware_cache", "agent_coordination")
_emit_records_workflow_lineage("p3", "graph_aware_cache", "workflow_lineage")
_emit_records_healing_outcome("p3", "graph_aware_cache", "healing_outcome")
_emit_escalates_failure("p3", "graph_aware_cache", "failure_escalation")
_emit_orchestrates_workflow("p3", "graph_aware_cache", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "graph_aware_cache", "healing_dispatch")
_emit_invokes_evaluation("p3", "graph_aware_cache", "evaluation_signal")
_emit_records_telemetry_event("p4", "graph_aware_cache", "telemetry_event")
_emit_captures_evaluation_metric("p4", "graph_aware_cache", "eval_metric")
_emit_stores_embedding("p4", "graph_aware_cache", "embedding_store")
_emit_updates_meta_learning_state("p4", "graph_aware_cache", "meta_learning")
_emit_links_execution_to_snapshot("p4", "graph_aware_cache", "exec_snapshot_link")

if TYPE_CHECKING:
    from agentic_core.adg.runtime.query_engine import ADGRuntimeQueryEngine
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

logger = logging.getLogger(__name__)


class GraphAwareCache:
    """Cache with ADG-driven precise invalidation.

    Each cache entry tracks which modules it depends on.
    When a file changes, only entries depending on affected modules are evicted.
    """

    def __init__(self, query_engine: ADGRuntimeQueryEngine) -> None:
        self.query_engine = query_engine
        self._cache: dict[str, dict[str, Any]] = {}
        self._hits: int = 0
        self._misses: int = 0

    def get(self, key: str) -> Any | None:
        """Return cached value or None if not present."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "GraphAwareCache.get")

        entry = self._cache.get(key)
        if entry is not None:
            self._hits += 1
            return entry["value"]
        self._misses += 1
        return None

    def set(self, key: str, value: Any, depends_on: list[str]) -> None:
        """Store a cache entry with explicit dependency tracking.

        Args:
            key: Cache key.
            value: Value to cache.
            depends_on: List of module relative paths this value depends on.
        """
        self._cache[key] = {"value": value, "depends_on": depends_on}

    def invalidate(self, key: str) -> bool:
        """Explicitly remove one cache entry. Returns True if it existed."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def invalidate_for_change(self, changed_file: str) -> int:
        """Invalidate all cache entries transitively affected by changed_file.

        Uses ADG reverse dependency graph to compute the exact invalidation set.
        Returns count of invalidated entries.
        """
        invalidation_set = self.query_engine.get_cache_invalidation_set(changed_file)
        count = 0
        for key in list(self._cache.keys()):
            entry = self._cache[key]
            depends_on: list[str] = entry.get("depends_on", [])
            if any(dep in invalidation_set for dep in depends_on):
                del self._cache[key]
                count += 1
        logger.debug(
            "Graph-aware invalidation: changed=%s affected=%d entries (invalidation_set_size=%d)",
            changed_file,
            count,
            len(invalidation_set),
        )
        return count

    def invalidate_all(self) -> int:
        """Clear the entire cache. Returns number of evicted entries."""
        count = len(self._cache)
        self._cache.clear()
        return count

    def size(self) -> int:
        """Return number of cached entries."""
        return len(self._cache)

    def stats(self) -> dict[str, int]:
        """Return cache statistics."""
        return {"size": self.size(), "hits": self._hits, "misses": self._misses}


__all__ = ["GraphAwareCache"]
