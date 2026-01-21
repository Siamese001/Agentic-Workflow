from __future__ import annotations
"""
Simulation & Scenario Schemas
=============================
Defines the models for running system simulations and capturing
outcomes. Used for testing agentic behavior in sandbox environments.
"""

from typing import Any, Dict

from pydantic import BaseModel, Field


class SimScenario(BaseModel):
    """Definition of a simulation scenario for system testing."""
    id: str = Field(..., description="Unique identifier for the scenario")
    description: str = Field(..., description="Human-readable summary of the test case")
    initial_context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Initial SignalContext state for the simulation"
    )
    execution_profile_name: str = Field(..., description="Target execution profile (e.g., 'standard', 'fast')")
    run_count: int = Field(default=1, ge=1, description="Number of iterations to perform")

class SimOutcome(BaseModel):
    """Aggregate results from a simulation run."""
    scenario_id: str = Field(..., description="ID of the simulated scenario")
    average_scores: Dict[str, float] = Field(default_factory=dict, description="Metric averages across runs")
    safety_incidents: int = Field(default=0, description="Total count of safety violations")
    agent_conflict_count: int = Field(default=0, description="Count of inter-agent consensus failures")
