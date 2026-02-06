from __future__ import annotations

"""
Simulation & Scenario Schemas
=============================
Defines the models for running system simulations and capturing
outcomes. Used for testing agentic behavior in sandbox environments.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SimScenario(BaseModel):
    """Definition of a simulation scenario for system testing."""

    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(..., description="Unique identifier for the scenario")
    description: str = Field(..., description="Human-readable summary of the test case")
    initial_context: dict[str, Any] = Field(
        default_factory=dict, description="Initial SignalContext state for the simulation"
    )
    execution_profile_name: str = Field(
        ..., description="Target execution profile (e.g., 'standard', 'fast')"
    )
    run_count: int = Field(default=1, ge=1, description="Number of iterations to perform")

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str) -> str:
        """[HARDENED] Ensure description is not empty."""
        if not value.strip():
            raise ValueError("Scenario description cannot be empty")
        return value.strip()


class SimOutcome(BaseModel):
    """Aggregate results from a simulation run."""

    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    scenario_id: str = Field(..., description="ID of the simulated scenario")
    average_scores: dict[str, float] = Field(default_factory=dict, description="Metric averages across runs")
    safety_incidents: int = Field(default=0, description="Total count of safety violations")
    agent_conflict_count: int = Field(default=0, description="Count of inter-agent consensus failures")
