"""
Optimization Strategy Engine - Early stopping & pruning logic
Refactored from optimization_strategies.py
"""

from __future__ import annotations

import logging
from typing import Any

from apps_rg.engines.base.BaseRGEngine import BaseRGEngine

Logger = logging.getLogger(__name__)


class OptimizationStrategyEngine(BaseRGEngine):
    """
    Optimization Strategy - Early stopping and pruning decisions.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="ORCHESTRATION.OPTIMIZATION")

    async def execute(
        self,
        iteration_count: int,
        quality_score: float,
        budget_remaining: float,
    ) -> dict[str, Any]:
        """
        Determine if optimization should continue or stop early.
        """
        self._mcp_audit("optimization_check", {"iteration": iteration_count, "score": quality_score})

        decision = {"should_continue": True, "reason": "", "pruning_recommendations": []}

        # Early stopping conditions
        if quality_score >= 0.95:
            decision["should_continue"] = False
            decision["reason"] = "Quality threshold achieved"
        elif iteration_count >= 5:
            decision["should_continue"] = False
            decision["reason"] = "Max iterations reached"
        elif budget_remaining < 0.1:
            decision["should_continue"] = False
            decision["reason"] = "Budget exhausted"

        # Pruning recommendations
        if quality_score < 0.7 and iteration_count > 2:
            decision["pruning_recommendations"].append("Consider template change")

        if decision["should_continue"]:
            self.record_pass("Optimization continues", data=decision)
        else:
            self.record_pass(f"Optimization stopped: {decision['reason']}", data=decision)

        return decision
