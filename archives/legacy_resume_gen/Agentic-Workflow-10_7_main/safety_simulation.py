"""Safety simulation models."""

from pydantic import BaseModel

from .simulation_base import SimulationInput, SimulationResult


class SafetySimRequest(SimulationInput):
    """Input payload for safety simulation."""

    text: str


class SafetySimMetrics(BaseModel):
    """Metrics produced by safety simulations."""

    pii_risk: float
    injection_risk: float
    bias_risk: float


class SafetySimResult(SimulationResult):
    """Result model for safety simulations."""

    pass
