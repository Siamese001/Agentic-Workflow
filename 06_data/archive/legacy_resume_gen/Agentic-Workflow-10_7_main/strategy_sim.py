"""Synthetic strategy simulator."""

import random
from typing import Any

from simulations.models.strategy_simulation import (
    StrategySimMetrics,
    StrategySimRequest,
    StrategySimResult,
)
from simulations.utils import model_to_payload


class StrategySimulator:
    """Runs a lightweight strategy simulation."""

    async def run(self, request: StrategySimRequest) -> StrategySimResult:
        metrics = StrategySimMetrics(
            clarity_score=round(random.uniform(0.5, 1.0), 3),
            alignment_score=round(random.uniform(0.3, 1.0), 3),
            risk_score=round(random.uniform(0.0, 0.7), 3),
            notes=["synthetic simulation only"],
        )
        strategy_name = None
        strategy_plan: Any = request.strategy_plan or {}
        if isinstance(strategy_plan, dict):
            strategy_name = strategy_plan.get("strategy_name")
        return StrategySimResult(
            simulation_id=request.simulation_id,
            success=True,
            metrics=model_to_payload(metrics),
            details={"strategy_preview": strategy_name},
        )
