from __future__ import annotations

"""
Refactored Cognitive Node - Coordinator Pattern

Orchestrates PerceptionNode, ReasoningNode, and ActionNode with:
- Parallel/async execution
- Lazy evaluation for simple intents
- Output caching
- Per-node performance monitoring
"""


import asyncio
import hashlib
import time
from typing import Any

from .ActionNode import ActionNode
from .PerceptionNode import PerceptionNode
from .ReasoningNode import ReasoningNode


class CognitiveNodeRefactored:
    """
    Refactored cognitive node - coordinator pattern.

    Decomposes monolithic CognitiveNode into focused sub-nodes:
    - PerceptionNode: Input processing
    - ReasoningNode: Thought generation
    - ActionNode: Execution

    Features:
    - Parallel/async execution
    - Lazy evaluation (simple intent → skip heavy reasoning)
    - Output caching (hash-based)
    - Per-node monitoring (metrics)
    """

    def __init__(self):
        """Initialize refactored cognitive node."""
        self.perception = PerceptionNode()
        self.reasoning = ReasoningNode()
        self.action = ActionNode()

        self.cache: dict[str, dict[str, Any]] = {}
        self.node_metrics = {
            "perception": {"calls": 0, "total_time": 0.0},
            "reasoning": {"calls": 0, "total_time": 0.0},
            "action": {"calls": 0, "total_time": 0.0},
        }
        self.total_processes = 0
        self.lazy_evaluations = 0

    def process(self, raw_input: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """
        Sequential cognitive processing (baseline).

        Args:
            raw_input: Raw user input
            context: Current context

        Returns:
            Final output
        """
        self.total_processes += 1

        # Check cache
        cache_key = self._make_cache_key(raw_input, context)
        if cache_key in self.cache:
            return self.cache[cache_key].copy()

        # Sequential pipeline
        start = time.time()
        perceived = self.perception.process(raw_input, context)
        self._record_metric("perception", time.time() - start)

        # Lazy evaluation: Simple intent → skip heavy reasoning
        if self._is_simple_intent(perceived):
            self.lazy_evaluations += 1
            start = time.time()
            output = self.action.act_simple(perceived)
            self._record_metric("action", time.time() - start)
        else:
            # Full reasoning pipeline
            start = time.time()
            reasoned = self.reasoning.reason(perceived)
            self._record_metric("reasoning", time.time() - start)

            start = time.time()
            output = self.action.act(reasoned)
            self._record_metric("action", time.time() - start)

        # Cache result
        self.cache[cache_key] = output.copy()

        return output

    async def process_async(
        self, raw_input: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Parallel cognitive processing with async/await.

        Enables:
        - Parallel perception + memory prefetch
        - Lazy evaluation (skip reasoning for simple intents)
        - Async tool execution

        Args:
            raw_input: Raw user input
            context: Current context

        Returns:
            Final output
        """
        self.total_processes += 1

        # Check cache
        cache_key = self._make_cache_key(raw_input, context)
        if cache_key in self.cache:
            return self.cache[cache_key].copy()

        # Parallel perception + memory prefetch
        start = time.time()
        perception_task = asyncio.create_task(self.perception.process_async(raw_input, context))
        memory_task = asyncio.create_task(self._lazy_memory_prefetch(context))

        perceived = await perception_task
        memory = await memory_task
        perceived["memory"] = memory
        self._record_metric("perception", time.time() - start)

        # Lazy evaluation: Simple intent → skip heavy reasoning
        if self._is_simple_intent(perceived):
            self.lazy_evaluations += 1
            start = time.time()
            output = await asyncio.to_thread(self.action.act_simple, perceived)
            self._record_metric("action", time.time() - start)
        else:
            # Full async reasoning pipeline
            start = time.time()
            reasoned = await self.reasoning.reason_async(perceived)
            self._record_metric("reasoning", time.time() - start)

            start = time.time()
            output = await self.action.act_async(reasoned)
            self._record_metric("action", time.time() - start)

        # Cache result
        self.cache[cache_key] = output.copy()

        return output

    def _make_cache_key(self, raw_input: dict[str, Any], context: dict[str, Any]) -> str:
        """
        Create stable cache key from input and context.

        Args:
            raw_input: Raw input
            context: Context

        Returns:
            Cache key
        """
        input_str = str(sorted(raw_input.items()))
        context_str = str(sorted(context.items()))
        key_input = f"{input_str}|{context_str}"
        return hashlib.sha256(key_input.encode()).hexdigest()

    def _is_simple_intent(self, perceived: dict[str, Any]) -> bool:
        """
        Determine if intent is simple (lazy evaluation).

        Args:
            perceived: Perceived state

        Returns:
            True if simple intent
        """
        # Heuristic: Short query + high confidence + known intent
        query_len = len(perceived.get("query", ""))
        confidence = perceived.get("confidence", 0.0)
        intent = perceived.get("intent", "")

        return query_len < 50 and confidence > 0.8 and intent in ["action", "memory"]

    async def _lazy_memory_prefetch(self, context: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Lazy memory prefetch (background task).

        Args:
            context: Current context

        Returns:
            Prefetched memory items
        """
        # Simulate async memory retrieval
        await asyncio.sleep(0.01)  # Placeholder
        return context.get("memory", [])

    def _record_metric(self, node_name: str, duration: float) -> None:
        """
        Record node performance metric.

        Args:
            node_name: Node name (perception, reasoning, action)
            duration: Execution duration
        """
        if node_name in self.node_metrics:
            self.node_metrics[node_name]["calls"] += 1
            self.node_metrics[node_name]["total_time"] += duration

    def get_statistics(self) -> dict[str, Any]:
        """Get cognitive node statistics."""
        stats = {
            "total_processes": self.total_processes,
            "lazy_evaluations": self.lazy_evaluations,
            "lazy_rate": (self.lazy_evaluations / self.total_processes * 100)
            if self.total_processes > 0
            else 0,
            "cache_size": len(self.cache),
            "nodes": {},
        }

        # Per-node statistics
        for node_name, metrics in self.node_metrics.items():
            calls = metrics["calls"]
            total_time = metrics["total_time"]
            avg_time = total_time / calls if calls > 0 else 0.0

            stats["nodes"][node_name] = {
                "calls": calls,
                "total_time": total_time,
                "avg_time": avg_time,
            }

        # Sub-node statistics
        stats["perception_stats"] = self.perception.get_statistics()
        stats["reasoning_stats"] = self.reasoning.get_statistics()
        stats["action_stats"] = self.action.get_statistics()

        return stats

    def clear_cache(self) -> None:
        """Clear output cache."""
        self.cache.clear()


# Global instance
cognitive_node_refactored = CognitiveNodeRefactored()
