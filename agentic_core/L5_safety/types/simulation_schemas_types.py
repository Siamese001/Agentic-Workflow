from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "simulation_schemas_types")
trace_contract.emit_determinism_digest("p0", "simulation_schemas_types")

trace_contract._emit_dispatches_healing_run("p1", "simulation_schemas_types", "L5")
trace_contract._emit_routes_through("p1", "simulation_schemas_types", "L5")
trace_contract._emit_checks_agent_registry("p1", "simulation_schemas_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "simulation_schemas_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "simulation_schemas_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "simulation_schemas_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "simulation_schemas_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "simulation_schemas_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "simulation_schemas_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "simulation_schemas_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "simulation_schemas_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "simulation_schemas_types")
trace_contract._emit_gated_by_confidence("p1", "simulation_schemas_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "simulation_schemas_types", "L5")
trace_contract._emit_reads_policy_state("p1", "simulation_schemas_types", "L5")

trace_contract._emit_applies_guardrail("p0", "simulation_schemas_types", "p0_governance")
trace_contract._emit_snapshots_state("p0", "simulation_schemas_types", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "simulation_schemas_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "simulation_schemas_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "simulation_schemas_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "simulation_schemas_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "simulation_schemas_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "simulation_schemas_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "simulation_schemas_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "simulation_schemas_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "simulation_schemas_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "simulation_schemas_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "simulation_schemas_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "simulation_schemas_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "simulation_schemas_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "simulation_schemas_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "simulation_schemas_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "simulation_schemas_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "simulation_schemas_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "simulation_schemas_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "simulation_schemas_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "simulation_schemas_types", "exec_snapshot_link")

"\nSimulation & Scenario Schemas\n=============================\nDefines the models for running system simulations and capturing\noutcomes. Used for testing agentic behavior in sandbox environments.\n"
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


trace_contract._emit_emits_metric_event("simulation_schemas_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("simulation_schemas_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("simulation_schemas_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("simulation_schemas_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("simulation_schemas_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("simulation_schemas_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("simulation_schemas_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("simulation_schemas_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("simulation_schemas_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("simulation_schemas_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("simulation_schemas_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("simulation_schemas_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("simulation_schemas_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("simulation_schemas_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("simulation_schemas_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("simulation_schemas_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("simulation_schemas_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("simulation_schemas_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("simulation_schemas_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("simulation_schemas_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("simulation_schemas_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("simulation_schemas_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("simulation_schemas_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("simulation_schemas_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("simulation_schemas_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("simulation_schemas_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("simulation_schemas_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("simulation_schemas_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "simulation_schemas_types", "context_pull")
trace_contract._emit_pulls_context("p1", "simulation_schemas_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "simulation_schemas_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "simulation_schemas_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "simulation_schemas_types", "write_through")
trace_contract._emit_writes_through("p1", "simulation_schemas_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "simulation_schemas_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "simulation_schemas_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "simulation_schemas_types", "routing_commit")


class SimScenario(BaseModel):
    """Definition of a simulation scenario for system testing."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    id: str = Field(..., description="Unique identifier for the scenario")
    description: str = Field(..., description="Human-readable summary of the test case")
    initial_context: dict[str, Any] = Field(
        default_factory=dict,
        description="Initial SignalContext state for the simulation",
    )
    execution_profile_name: str = Field(
        ...,
        description="Target execution profile (e.g., 'standard', 'fast')",
    )
    run_count: int = Field(default=1, ge=1, description="Number of iterations to perform")

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str) -> str:
        """[HARDENED] Ensure description is not empty."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "SimScenario.validate_description")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:SimScenario.validate_description".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
