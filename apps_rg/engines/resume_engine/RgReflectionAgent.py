from dataclasses import dataclass
"""
RgReflectionAgent - Extracted for one-class-per-file pattern.

Originally from: ContentQualityAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""


from __future__ import annotations
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.L3_orchestration.mixins.L3SubatomicTestingMixin import SubatomicTestingMixin

@dataclass
class RgReflectionAgent(SubatomicTestingMixin, ResumeAgent, MCPHardenedMixin):
    """
    Learns from execution and records insights.

    Analyzes:
    - What worked
    - What failed
    - Patterns to remember
    """

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
        insights: dict = {
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
