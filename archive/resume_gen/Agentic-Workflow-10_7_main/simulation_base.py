"""Base models for simulations."""

from typing import Any, Dict, List

from pydantic import BaseModel, Field


class SimulationInput(BaseModel):
    """Base class for simulation input payloads."""

    simulation_id: str = Field(...)
    payload: Dict[str, Any] = Field(default_factory=dict)


class SimulationResult(BaseModel):
    """Base class for simulation results."""

    simulation_id: str
    success: bool
    metrics: Dict[str, Any] = Field(default_factory=dict)
    details: Dict[str, Any] = Field(default_factory=dict)


class SimulationBatchResult(BaseModel):
    """Aggregated simulation result container."""

    results: List[SimulationResult] = Field(default_factory=list)
