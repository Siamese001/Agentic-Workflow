from __future__ import annotations

from typing import Any, Dict

from pydantic import BaseModel


class SimScenario(BaseModel):
    id: str
    description: str
    initial_context: Dict[str, Any]
    execution_profile_name: str
    run_count: int


class SimOutcome(BaseModel):
    scenario_id: str
    average_scores: Dict[str, float]
    safety_incidents: int
    agent_conflict_count: int
