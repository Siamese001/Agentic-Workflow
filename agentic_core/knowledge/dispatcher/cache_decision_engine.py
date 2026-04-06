"""Cache Decision Engine.

Retains routing authority based on explicit policies.
Computes budgets and thresholds for retrieval decisions.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
)

log = logging.getLogger(__name__)


class CacheStrategy(Enum):
    """Cache strategy types."""
    CHECK_CACHE = "check_cache"
    BYPASS_CACHE = "bypass_cache"
    FORCE_REFRESH = "force_refresh"


class RetrievalStrategy(Enum):
    """Retrieval strategy types."""
    HYBRID = "hybrid"
    VECTOR_ONLY = "vector_only"
    SPARSE_ONLY = "sparse_only"
    CACHE_ONLY = "cache_only"


@dataclass
class CacheDecision:
    """Decision from cache decision engine."""
    query_id: str
    cache_strategy: CacheStrategy
    retrieval_strategy: RetrievalStrategy
    use_cache: bool
    check_freshness: bool
    freshness_band: str
    compute_budget: int  # tokens
    priority: int  # 1-10
    metadata: dict[str, Any] = field(default_factory=dict)


class CacheDecisionEngine:
    """Makes cache and retrieval decisions based on policies.

    The CacheDecisionEngine retains routing authority and makes
    decisions based on explicit policies rather than letting
    retrieval dictate execution.
    """

    def __init__(self):
        """Initialize the cache decision engine."""
        self._policies: list[dict[str, Any]] = []
        self._setup_default_policies()
        log.info("CacheDecisionEngine initialized")

    def _setup_default_policies(self):
        """Setup default decision policies."""
        self._policies = [
            {
                "name": "urgent_queries",
                "condition": lambda ctx: ctx.get("urgency", 0) > 0.7,
                "decision": {
                    "cache_strategy": CacheStrategy.BYPASS_CACHE,
                    "retrieval_strategy": RetrievalStrategy.HYBRID,
                    "freshness_band": "realtime",
                    "priority": 10,
                },
            },
            {
                "name": "frequent_queries",
                "condition": lambda ctx: ctx.get("query_frequency", 0) > 5,
                "decision": {
                    "cache_strategy": CacheStrategy.CHECK_CACHE,
                    "retrieval_strategy": RetrievalStrategy.CACHE_ONLY,
                    "freshness_band": "hourly",
                    "priority": 3,
                },
            },
            {
                "name": "analytical_queries",
                "condition": lambda ctx: ctx.get("intent") == "analytical",
                "decision": {
                    "cache_strategy": CacheStrategy.CHECK_CACHE,
                    "retrieval_strategy": RetrievalStrategy.HYBRID,
                    "freshness_band": "daily",
                    "priority": 5,
                },
            },
            {
                "name": "policy_queries",
                "condition": lambda ctx: ctx.get("domain") == "policy",
                "decision": {
                    "cache_strategy": CacheStrategy.CHECK_CACHE,
                    "retrieval_strategy": RetrievalStrategy.HYBRID,
                    "freshness_band": "daily",
                    "priority": 6,
                },
            },
        ]

    def decide(
        self,
        query_id: str,
        query_context: dict[str, Any],
        scope_metadata: dict[str, Any],
    ) -> CacheDecision:
        """Make cache and retrieval decision.

        Args:
            query_id: Unique query identifier
            query_context: Query context with intent, urgency, etc.
            scope_metadata: Scope metadata from gates

        Returns:
            CacheDecision with routing strategy
        """
        trace_id = f"cache_dec_{query_id}"
        _emit_records_execution_trace(
            trace_id, LayerSegment.L1_REASONING, "CacheDecisionEngine.decide"
        )

        # Find matching policy
        decision_params = self._find_matching_policy(query_context)

        # Override with scope metadata if present
        freshness = scope_metadata.get("freshness_band", decision_params.get("freshness_band", "daily"))

        # Calculate compute budget based on priority
        priority = decision_params.get("priority", 5)
        budget = self._calculate_budget(priority, query_context)

        decision = CacheDecision(
            query_id=query_id,
            cache_strategy=decision_params.get("cache_strategy", CacheStrategy.CHECK_CACHE),
            retrieval_strategy=decision_params.get("retrieval_strategy", RetrievalStrategy.HYBRID),
            use_cache=decision_params.get("cache_strategy") != CacheStrategy.BYPASS_CACHE,
            check_freshness=True,
            freshness_band=freshness,
            compute_budget=budget,
            priority=priority,
            metadata={
                "matched_policy": decision_params.get("policy_name", "default"),
                "query_context": query_context,
                "scope_metadata": scope_metadata,
            },
        )

        _emit_records_telemetry_event(
            "cache_decision",
            f"{decision.cache_strategy.value}_{decision.retrieval_strategy.value}"
        )

        log.debug(f"Cache decision for {query_id}: {decision.cache_strategy.value}")
        return decision

    def add_policy(
        self,
        name: str,
        condition: callable,
        decision: dict[str, Any],
    ) -> None:
        """Add a custom policy.

        Args:
            name: Policy name
            condition: Function that takes context and returns bool
            decision: Dictionary with cache_strategy, retrieval_strategy, etc.
        """
        self._policies.append({
            "name": name,
            "condition": condition,
            "decision": decision,
        })
        log.info(f"Added policy: {name}")

    def _find_matching_policy(self, context: dict[str, Any]) -> dict[str, Any]:
        """Find first matching policy for context."""
        for policy in self._policies:
            try:
                if policy["condition"](context):
                    result = dict(policy["decision"])
                    result["policy_name"] = policy["name"]
                    return result
            except Exception as e:
                log.warning(f"Policy {policy['name']} evaluation error: {e}")

        # Default decision
        return {
            "policy_name": "default",
            "cache_strategy": CacheStrategy.CHECK_CACHE,
            "retrieval_strategy": RetrievalStrategy.HYBRID,
            "freshness_band": "daily",
            "priority": 5,
        }

    def _calculate_budget(self, priority: int, context: dict[str, Any]) -> int:
        """Calculate compute budget based on priority."""
        base_budget = 1000  # tokens

        # Adjust by priority (1-10)
        priority_multiplier = priority / 5.0

        # Adjust by complexity
        complexity = context.get("complexity", 0.5)
        complexity_multiplier = 0.5 + complexity

        budget = int(base_budget * priority_multiplier * complexity_multiplier)
        return min(budget, 5000)  # Cap at 5000 tokens


# Global instance
_global_engine: CacheDecisionEngine | None = None


def get_cache_decision_engine() -> CacheDecisionEngine:
    """Get or create the global cache decision engine."""
    global _global_engine
    if _global_engine is None:
        _global_engine = CacheDecisionEngine()
    return _global_engine


def make_cache_decision(
    query_id: str,
    query_context: dict[str, Any],
    scope_metadata: dict[str, Any],
) -> CacheDecision:
    """Convenience function to make cache decision."""
    return get_cache_decision_engine().decide(query_id, query_context, scope_metadata)
