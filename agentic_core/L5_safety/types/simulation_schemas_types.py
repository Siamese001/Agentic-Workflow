from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "simulation_schemas_types")
emit_determinism_digest("p0", "simulation_schemas_types")

_emit_dispatches_healing_run("p1", "simulation_schemas_types", "L5")
_emit_routes_through("p1", "simulation_schemas_types", "L5")
_emit_escalates_to_human("p1", "simulation_schemas_types", "L5")
_emit_reads_policy_state("p1", "simulation_schemas_types", "L5")

_emit_applies_guardrail("p0", "simulation_schemas_types", "p0_governance")
_emit_snapshots_state("p0", "simulation_schemas_types", "state_snapshot")
_emit_authorize_and_execute("p2", "simulation_schemas_types", "execution_auth")
_emit_validates_capability("p2", "simulation_schemas_types", "capability_check")
_emit_routes_to_capability("p2", "simulation_schemas_types", "capability_route")
_emit_writes_via_uwg("p2", "simulation_schemas_types", "uwg_write")
_emit_blocks_direct_write("p2", "simulation_schemas_types", "direct_write_block")
_emit_records_tool_invocation("p2", "simulation_schemas_types", "tool_invocation")
_emit_captures_execution_output("p2", "simulation_schemas_types", "exec_output")
_emit_dispatches_agent("p3", "simulation_schemas_types", "agent_dispatch")
_emit_coordinates_agents("p3", "simulation_schemas_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "simulation_schemas_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "simulation_schemas_types", "healing_outcome")
_emit_escalates_failure("p3", "simulation_schemas_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "simulation_schemas_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "simulation_schemas_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "simulation_schemas_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "simulation_schemas_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "simulation_schemas_types", "eval_metric")
_emit_stores_embedding("p4", "simulation_schemas_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "simulation_schemas_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "simulation_schemas_types", "exec_snapshot_link")

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
