from __future__ import annotations

from typing import Any, Dict

from archives.legacy_resume_gen.Older Microservices Models.v10.6.pydantic import BaseModel


class SimScenario(BaseModel):
    id: str
    description: str
    initial_context: Dict[str, object]
    execution_profile_name: str
    run_count: int


class SimOutcome(BaseModel):
    scenario_id: str
    average_scores: Dict[str, float]
    safety_incidents: int
    agent_conflict_count: int



