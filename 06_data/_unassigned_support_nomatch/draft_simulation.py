"""Draft simulation models."""

from typing import Any, Dict

from pydantic import BaseModel

from .simulation_base import SimulationInput, SimulationResult


class DraftSimRequest(SimulationInput):
    """Input payload for draft simulation."""

    draft_sections: Dict[str, Any]


class DraftSimMetrics(BaseModel):
    """Metrics produced by draft simulations."""

    entropy: float
    cohesion: float
    rhythm_score: float


class DraftSimResult(SimulationResult):
    """Result model for draft simulations."""

    pass
