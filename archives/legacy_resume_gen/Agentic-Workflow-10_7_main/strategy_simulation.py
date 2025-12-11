"""Strategy simulation models."""

from typing import Any, Dict, List

from archives.legacy_resume_gen.Older Microservices Models.v10.6.pydantic import BaseModel, Field

# from archives.legacy_resume_gen.Agentic-Workflow-10_7_main.simulation_base import SimulationInput, SimulationResult  # INVALID: Cannot import from path with hyphens


class StrategySimRequest(SimulationInput):
    """Input payload for strategy simulation."""

    job_title: str
    company: str
    strategy_plan: Dict[str, object]


class StrategySimMetrics(BaseModel):
    """Metrics produced by a strategy simulation."""

    clarity_score: float
    alignment_score: float
    risk_score: float
    notes: List[str] = Field(default_factory=list)


class StrategySimResult(SimulationResult):
    """Result model for strategy simulations."""

    metrics: Dict[str, object]
    details: Dict[str, object]
