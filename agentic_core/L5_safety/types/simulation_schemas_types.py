from __future__ import annotations

"\nSimulation & Scenario Schemas\n=============================\nDefines the models for running system simulations and capturing\noutcomes. Used for testing agentic behavior in sandbox environments.\n"
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)


class SimScenario(BaseModel):
    """Definition of a simulation scenario for system testing."""

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
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "SimScenario.validate_description")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:SimScenario.validate_description".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if not value.strip():
            raise ValueError("Scenario description cannot be empty")
        return value.strip()


class SimOutcome(BaseModel):
    """Aggregate results from a simulation run."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    scenario_id: str = Field(..., description="ID of the simulated scenario")
    average_scores: dict[str, float] = Field(default_factory=dict, description="Metric averages across runs")
    safety_incidents: int = Field(default=0, description="Total count of safety violations")
    agent_conflict_count: int = Field(default=0, description="Count of inter-agent consensus failures")
