"""RgReflectionAgent — RG domain reflection agent with Phase 5 meta-learning.

Originally from: ContentQualityAgent.py (Surgical Extraction 2026-01-06)
Refactored: 2026-03-11 (P2-A) — now subclasses BaseReflectionAgent.

PHASE 5 META-LEARNING (Feb 2026):
- Redis/Pinecone integration for reflection pattern memory
- Execution insight caching and recall
- Quality pattern learning for resume generation
- Cross-session learning persistence
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge
from apps_shared.reasoning.BaseReflectionAgent import BaseReflectionAgent

Logger = logging.getLogger(__name__)


@dataclass
class RgReflectionAgent(BaseReflectionAgent):
    """Learns from RG execution and records insights.

    [PHASE 5] Meta-Learning Integration:
    - Caches execution insights for future recall
    - Learns quality patterns from successful generations
    - Persists learning across sessions via Redis/Pinecone

    Inherits execute() skeleton from BaseReflectionAgent.
    Overrides _post_reflect() to add quality scoring and context recording.
    """

    def __post_init__(self) -> None:
        """Initialize reflection agent."""
        super().__post_init__()
        Logger.debug(f"[{self.__class__.__name__}] Meta-Learning reflection agent initialized")
        try:
            bridge = GraphMemoryBridge.get_instance()
            bridge.create_agent_entity(
                agent_name=self.__class__.__name__,
                agent_type="ReflectionAgent",
                observations=["RG reflection agent with meta-learning and quality scoring"],
            )
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.debug(f"[{self.__class__.__name__}] KG registration skipped: {e}")

    def _post_reflect(self, passed_agents: list[str], failed_agents: list[str], converged: bool) -> None:
        """RG-specific post-reflection: quality scoring and context recording."""
        insights: dict[str, Any] = {
            "cycle": self.ctx.current_cycle,
            "signals_at_end": list(self.ctx.signals),
            "failed_agents": failed_agents,
            "modified_sections": list(self.ctx.modified_sections),
            "budget_used": self.ctx.budget.current_cost,
            "converged": converged,
        }
        if converged:
            insights["outcome"] = "success"
            if self.ctx.current_resume:
                quality_score: float = self._estimate_quality_score()
                self.ctx.record_success(self.ctx.current_resume, quality_score)
                if quality_score < 0.6:
                    best_practices = self._search_external_best_practices(
                        "resume writing quality improvement"
                    )
                    if best_practices:
                        insights["external_best_practices"] = best_practices
        else:
            insights["outcome"] = "needs_more_cycles"
            best_practices = self._search_external_best_practices(
                "outreach reflection improvement techniques"
            )
            if best_practices:
                insights["external_best_practices"] = best_practices
        self.ctx.results["reflection"] = insights
        self._persist_reflection_to_kg(insights, passed_agents, failed_agents, converged)

    def _persist_reflection_to_kg(
        self, insights: dict[str, Any], passed_agents: list[str], failed_agents: list[str], converged: bool
    ) -> None:
        """Persist reflection outcome to Memory MCP knowledge graph."""
        try:
            bridge = GraphMemoryBridge.get_instance()
            outcome = insights.get("outcome", "unknown")
            cycle = insights.get("cycle", 0)
            obs = f"Cycle={cycle} outcome={outcome} passed={len(passed_agents)} failed={len(failed_agents)} budget={insights.get('budget_used', 0):.4f}"
            bridge.add_observation(entity_name=self.__class__.__name__, observation=obs)
            if converged and self.ctx.current_resume:
                bridge.create_relation(
                    from_entity=self.__class__.__name__,
                    to_entity="ResumeDocument",
                    relation_type="REFLECTS_ON",
                )
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.debug(f"[{self.__class__.__name__}] KG reflection persistence skipped: {e}")

    def _search_external_best_practices(self, topic: str) -> list[dict[str, Any]]:
        """Search for external best practices via Brave Search MCP when quality is low.

        Args:
            topic: The topic to search for

        Returns:
            List of result dicts with title/url/description, or empty list on failure
        """
        try:
            import asyncio

            from agentic_core.L3_orchestration.reasoning.mcp_manager import MCPConnectionManager

            mcp = MCPConnectionManager()
            args = {"query": topic, "count": 3}
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import concurrent.futures

                    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                        future = pool.submit(asyncio.run, mcp.call_tool("brave_search", args))
                        # guardian: allow-magic-config
                        result = future.result(timeout=10)
                else:
                    result = loop.run_until_complete(mcp.call_tool("brave_search", args))
            # guardian: allow-silent-swallow
            except Exception:
                result = {}
            if isinstance(result, dict) and result.get("results"):
                Logger.info(
                    f"[{self.__class__.__name__}] Brave Search: {len(result['results'])} results for '{topic}'"
                )
                return result["results"][:3]
            return []
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.debug(f"[{self.__class__.__name__}] Brave Search skipped: {e}")
            return []

    def _estimate_quality_score(self) -> float:
        """Estimate quality score as passed/total agents ratio."""
        total_agents: int = len(self.ctx.results)
        if total_agents == 0:
            return 0.5
        passed = sum(1 for r in self.ctx.results.values() if r.get("passed", False))
        return passed / total_agents

    def ml_cache_execution_insight(self, insight_id: str, insight_data: dict[str, Any]) -> bool:
        """
        Cache an execution insight for future recall.

        Args:
            insight_id: Unique insight identifier
            insight_data: Insight data (cycle, signals, outcome, etc.)

        Returns:
            True if cached successfully
        """
        cache_key = f"execution_insight:{insight_id}"
        return self.ml_cache_set(cache_key, insight_data)

    # guardian: allow-type-erasure
    def ml_recall_execution_insight(self, insight_id: str) -> dict[str, Any] | None:
        """
        Recall a cached execution insight.

        Args:
            insight_id: Unique insight identifier

        Returns:
            Cached insight data or None
        """
        cache_key = f"execution_insight:{insight_id}"
        return self.ml_cache_get(cache_key)

    def ml_cache_quality_pattern(self, pattern_id: str, pattern_data: dict[str, Any]) -> bool:
        """
        Cache a successful quality pattern.

        Args:
            pattern_id: Unique pattern identifier
            pattern_data: Quality pattern data

        Returns:
            True if cached successfully
        """
        cache_key = f"quality_pattern:{pattern_id}"
        return self.ml_cache_set(cache_key, pattern_data)

    # guardian: allow-type-erasure
    def ml_recall_quality_pattern(self, pattern_id: str) -> dict[str, Any] | None:
        """
        Recall a cached quality pattern.

        Args:
            pattern_id: Unique pattern identifier

        Returns:
            Cached pattern data or None
        """
        cache_key = f"quality_pattern:{pattern_id}"
        return self.ml_cache_get(cache_key)

    def ml_record_reflection_success(
        self, context_hash: str, insights: dict[str, Any], quality_score: float
    ) -> bool:
        """
        Record a successful reflection for future learning.

        Args:
            context_hash: Hash of the execution context
            insights: Reflection insights
            quality_score: Quality score achieved

        Returns:
            True if recorded successfully
        """
        if quality_score >= 0.7:
            cache_key = f"reflection_success:{context_hash}"
            return self.ml_cache_set(cache_key, {"insights": insights, "quality_score": quality_score})
        return False

    # guardian: allow-type-erasure
    def ml_recall_similar_reflection(self, context_hash: str) -> dict[str, Any] | None:
        """
        Recall a similar successful reflection.

        Args:
            context_hash: Hash of the execution context

        Returns:
            Cached reflection data or None
        """
        cache_key = f"reflection_success:{context_hash}"
        return self.ml_cache_get(cache_key)
