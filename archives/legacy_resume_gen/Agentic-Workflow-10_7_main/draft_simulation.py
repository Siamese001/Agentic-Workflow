"""Draft simulation models."""

from typing import Any, Dict

from archives.legacy_resume_gen.Older Microservices Models.v10.6.pydantic import BaseModel

# from archives.legacy_resume_gen.Agentic-Workflow-10_7_main.simulation_base import SimulationInput, SimulationResult  # INVALID: Cannot import from path with hyphens


class DraftSimRequest(SimulationInput):
    """Input payload for draft simulation."""

    draft_sections: Dict[str, object]


class DraftSimMetrics(BaseModel):
    """Metrics produced by draft simulations."""

    entropy: float
    cohesion: float
    rhythm_score: float


class DraftSimResult(SimulationResult):
    """Result model for draft simulations."""

    pass
