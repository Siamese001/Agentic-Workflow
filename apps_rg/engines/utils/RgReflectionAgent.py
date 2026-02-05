"""
RgReflectionAgent - Extracted for one-class-per-file pattern.

Originally from: ContentQualityAgent.py
Extracted: 2026-01-06 (Surgical Extraction)

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

from apps_rg.shared.core.RGAgentBase import RGAgentBase

Logger = logging.getLogger(__name__)


@dataclass
class RgReflectionAgent(RGAgentBase):
    """
    Learns from execution and records insights.

    [PHASE 5] Meta-Learning Integration:
    - Caches execution insights for future recall
    - Learns quality patterns from successful generations
    - Persists learning across sessions via Redis/Pinecone
    - Domain-specific pattern matching (apps_rg)

    Analyzes:
    - What worked
    - What failed
    - Patterns to remember
    """

    def __post_init__(self) -> None:
        """Initialize reflection agent."""
        super().__post_init__()
        Logger.debug(f"[{self.__class__.__name__}] Meta-Learning reflection agent initialized")

    async def execute(self) -> None:
        """
        Execute reflection on system execution.

        Analyzes:
        - Cycle performance and convergence
        - Failed agents and signals
        - Budget usage and modifications
        - Overall outcome and quality

        Records insights for learning and improvement.
        """
        self.log("Reflecting on execution...")

        # Gather insights
        insights: dict[str, Any] = {
            "cycle": self.ctx.current_cycle,
            "signals_at_end": list(self.ctx.signals),
            "failed_agents": list(self.ctx.get_failed_results().keys()),
            "modified_sections": list(self.ctx.modified_sections),
            "budget_used": self.ctx.budget.current_cost,
            "converged": self.ctx.is_converged(),
        }

        # Determine success
        if self.ctx.is_converged():
            insights["outcome"] = "success"
            self.log("✨ System converged successfully")

            # Record for learning
            if self.ctx.current_resume:
                quality_score: float = self._estimate_quality_score()
                self.ctx.record_success(self.ctx.current_resume, quality_score)
        else:
            insights["outcome"] = "needs_more_cycles"
            self.log(f"🔄 More cycles needed (signals: {len(self.ctx.signals)})")

        self.ctx.results["reflection"] = insights
        self.record_pass("Reflection complete", data=insights)

    def _estimate_quality_score(self) -> float:
        """
        Estimate quality score based on agent results.

        Returns:
            Quality score (0-1) based on passed/total agents ratio
        """
        total_agents: int = len(self.ctx.results)
        if total_agents == 0:
            return 0.5

        passed = sum(1 for r in self.ctx.results.values() if r.get("passed", False))
        return passed / total_agents

    def heal_repository(self) -> dict:
        """Invoke healing chain via super()."""
        return super().heal_repository()

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """Heal violations detected by RgReflectionAgent."""
        violation_type = violation.get("type", "unknown")
        try:
            return {
                "status": "skipped",
                "details": (f"RgReflectionAgent heal() not yet implemented for {violation_type}"),
                "artifacts": [],
                "errors": [],
            }
        except Exception as e:
            return {
                "status": "failed",
                "details": f"RgReflectionAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }

    # ==================== PHASE 5: META-LEARNING METHODS ====================

    def ml_cache_execution_insight(
        self,
        insight_id: str,
        insight_data: dict[str, Any],
    ) -> bool:
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

    def ml_recall_execution_insight(
        self,
        insight_id: str,
    ) -> dict[str, Any] | None:
        """
        Recall a cached execution insight.

        Args:
            insight_id: Unique insight identifier

        Returns:
            Cached insight data or None
        """
        cache_key = f"execution_insight:{insight_id}"
        return self.ml_cache_get(cache_key)

    def ml_cache_quality_pattern(
        self,
        pattern_id: str,
        pattern_data: dict[str, Any],
    ) -> bool:
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

    def ml_recall_quality_pattern(
        self,
        pattern_id: str,
    ) -> dict[str, Any] | None:
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
        self,
        context_hash: str,
        insights: dict[str, Any],
        quality_score: float,
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
        if quality_score >= 0.7:  # Only cache high-quality reflections
            cache_key = f"reflection_success:{context_hash}"
            return self.ml_cache_set(
                cache_key,
                {
                    "insights": insights,
                    "quality_score": quality_score,
                },
            )
        return False

    def ml_recall_similar_reflection(
        self,
        context_hash: str,
    ) -> dict[str, Any] | None:
        """
        Recall a similar successful reflection.

        Args:
            context_hash: Hash of the execution context

        Returns:
            Cached reflection data or None
        """
        cache_key = f"reflection_success:{context_hash}"
        return self.ml_cache_get(cache_key)
