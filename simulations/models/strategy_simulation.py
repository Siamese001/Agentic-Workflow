"""Strategy simulation models."""

from typing import Any, Dict, List

from pydantic import BaseModel, Field

from .simulation_base import SimulationInput, SimulationResult


class StrategySimRequest(SimulationInput):
    """Input payload for strategy simulation."""

    job_title: str
    company: str
    strategy_plan: Dict[str, Any]


class StrategySimMetrics(BaseModel):
    """Metrics produced by a strategy simulation."""

    clarity_score: float
    alignment_score: float
    risk_score: float
    notes: List[str] = Field(default_factory=list)


class StrategySimResult(SimulationResult):
    """Result model for strategy simulations."""

    metrics: Dict[str, Any]
    details: Dict[str, Any]
