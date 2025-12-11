"""Safety simulation models."""

from archives.legacy_resume_gen.Older Microservices Models.v10.6.pydantic import BaseModel

# from archives.legacy_resume_gen.Agentic-Workflow-10_7_main.simulation_base import SimulationInput, SimulationResult  # INVALID: Cannot import from path with hyphens


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
