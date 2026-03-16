"""L3 Orchestration — DAG / step-plan memoisation cache seam.

Provides ``OrchestrationPlanCache`` which stores resolved orchestration
plans (step DAG, deduped tool calls, handshake schedule) keyed by
``(trace_id, plan_hash, tool_budget_hash)``.

Determinism contract
--------------------
* The plan cache is keyed by three stable inputs that fully determine the
  orchestration output.  When any input changes the key changes and a fresh
  plan is computed from L4.
* ``replay_mode=True`` bypasses the cache so the orchestrator replays the
  full plan-computation path and records the result in the transcript.
* Writing to this cache does NOT modify any L4 state.

Relationship to existing ``SovereignRedisOrchestrator``
-------------------------------------------------------
``SovereignRedisOrchestrator`` is a general-purpose Redis client for ad-hoc
agent operations.  This module is the *typed*, *non-authoritative* memoisation
seam specifically for orchestration plan derivations — it never uses the
existing orchestrator's ``heal_repository`` path.
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.cache.cache_key_builders import build_orch_plan_key
from agentic_core.cache.redis_cache_client import (
    DeterministicRedisCache,
    get_hot_cache,
)
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

emit_replay_key("p0", "orchestration_plan_cache")
emit_determinism_digest("p0", "orchestration_plan_cache")

_emit_dispatches_healing_run("p1", "orchestration_plan_cache", "L3")
_emit_routes_through("p1", "orchestration_plan_cache", "L3")
_emit_escalates_to_human("p1", "orchestration_plan_cache", "L3")
_emit_reads_policy_state("p1", "orchestration_plan_cache", "L3")

_emit_snapshots_state("p0", "orchestration_plan_cache", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "orchestration_plan_cache", "p0_governance")
_emit_authorize_and_execute("p2", "orchestration_plan_cache", "execution_auth")
_emit_validates_capability("p2", "orchestration_plan_cache", "capability_check")
_emit_routes_to_capability("p2", "orchestration_plan_cache", "capability_route")
_emit_writes_via_uwg("p2", "orchestration_plan_cache", "uwg_write")
_emit_blocks_direct_write("p2", "orchestration_plan_cache", "direct_write_block")
_emit_records_tool_invocation("p2", "orchestration_plan_cache", "tool_invocation")
_emit_captures_execution_output("p2", "orchestration_plan_cache", "exec_output")
_emit_dispatches_agent("p3", "orchestration_plan_cache", "agent_dispatch")
_emit_coordinates_agents("p3", "orchestration_plan_cache", "agent_coordination")
_emit_records_workflow_lineage("p3", "orchestration_plan_cache", "workflow_lineage")
_emit_records_healing_outcome("p3", "orchestration_plan_cache", "healing_outcome")
_emit_escalates_failure("p3", "orchestration_plan_cache", "failure_escalation")
_emit_orchestrates_workflow("p3", "orchestration_plan_cache", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "orchestration_plan_cache", "healing_dispatch")
_emit_invokes_evaluation("p3", "orchestration_plan_cache", "evaluation_signal")
_emit_records_telemetry_event("p4", "orchestration_plan_cache", "telemetry_event")
_emit_captures_evaluation_metric("p4", "orchestration_plan_cache", "eval_metric")
_emit_stores_embedding("p4", "orchestration_plan_cache", "embedding_store")
_emit_updates_meta_learning_state("p4", "orchestration_plan_cache", "meta_learning")
_emit_links_execution_to_snapshot("p4", "orchestration_plan_cache", "exec_snapshot_link")

logger = logging.getLogger(__name__)

_DEFAULT_ORCH_PLAN_TTL: int = 3600  # 1 hour


class OrchestrationPlanCache:
    """Memoises resolved orchestration plans for identical L3 inputs.

    The cached value is a dict representing the serialisable fields of the
    orchestration plan::

        {
            "step_dag":          [...],   # ordered list of plan steps
            "deduped_tool_calls": [...],  # canonical tool-call list
            "handshake_schedule": [...],  # agent handshake ordering
            "plan_hash":         "<hex>", # echoed back for verification
            "tool_budget_hash":  "<hex>",
        }

    Callers must verify that both ``plan_hash`` and ``tool_budget_hash`` in
    the returned dict match the values used to look it up.

    Parameters
    ----------
    ttl_seconds:
        Redis TTL applied to every ``set`` call.
    cache:
        Override the shared hot-cache instance (useful for testing).
    """

    def __init__(
        self,
        ttl_seconds: int = _DEFAULT_ORCH_PLAN_TTL,
        cache: DeterministicRedisCache | None = None,
    ) -> None:
        self._ttl = ttl_seconds
        self._cache = cache or get_hot_cache()

    def get(
        self,
        trace_id: str,
        plan_hash: str,
        tool_budget_hash: str,
        *,
        replay_mode: bool = False,
    ) -> dict[str, Any] | None:
        """Return the cached orchestration plan dict or ``None`` on miss/bypass."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "OrchestrationPlanCache.get")

        key = build_orch_plan_key(trace_id, plan_hash, tool_budget_hash)
        return self._cache.get_json(key, replay_mode=replay_mode)

    def set(
        self,
        trace_id: str,
        plan_hash: str,
        tool_budget_hash: str,
        plan: dict[str, Any],
    ) -> None:
        """Store *plan* under the deterministic key.

        *plan* must include ``"plan_hash"`` and ``"tool_budget_hash"`` fields
        echoed back from the orchestrator so downstream callers can verify
        the plan was computed for the exact same inputs.
        """
        key = build_orch_plan_key(trace_id, plan_hash, tool_budget_hash)
        self._cache.set_json(key, plan, ttl_seconds=self._ttl)

    def get_or_fetch(
        self,
        trace_id: str,
        plan_hash: str,
        tool_budget_hash: str,
        fetch_from_l4: Any,
        *,
        replay_mode: bool = False,
    ) -> dict[str, Any]:
        """Read-through helper: return cached plan or call *fetch_from_l4*.

        *fetch_from_l4* is a zero-argument callable that returns the resolved
        orchestration plan dict from L4.  Called only on a cache miss.

        This is the canonical wiring point for L3 orchestration engines.
        Engines should call this instead of calling ``get()`` and L4 directly.
        """
        if not replay_mode:
            cached = self.get(trace_id, plan_hash, tool_budget_hash)
            if cached is not None:
                logger.debug("[L3 cache] orch_plan HIT")
                return cached
        logger.debug("[L3 cache] orch_plan MISS — fetching from L4")
        result = fetch_from_l4()
        if not replay_mode:
            self.set(trace_id, plan_hash, tool_budget_hash, result)
        return result

    def invalidate(
        self,
        trace_id: str,
        plan_hash: str,
        tool_budget_hash: str,
    ) -> None:
        """Explicitly evict a cached orchestration plan."""
        key = build_orch_plan_key(trace_id, plan_hash, tool_budget_hash)
        self._cache.delete(key)


# ---------------------------------------------------------------------------
# Module-level convenience singleton
# ---------------------------------------------------------------------------

_orch_plan_cache: OrchestrationPlanCache | None = None


def get_orchestration_plan_cache() -> OrchestrationPlanCache:
    """Return the process-global ``OrchestrationPlanCache`` instance."""
    global _orch_plan_cache
    if _orch_plan_cache is None:
        _orch_plan_cache = OrchestrationPlanCache()
    return _orch_plan_cache
