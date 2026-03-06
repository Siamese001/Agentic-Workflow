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
        cached = self.get(trace_id, plan_hash, tool_budget_hash, replay_mode=replay_mode)
        if cached is not None:
            logger.debug("[L3 cache] orch_plan HIT")
            return cached
        logger.debug("[L3 cache] orch_plan MISS — fetching from L4")
        result = fetch_from_l4()
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
