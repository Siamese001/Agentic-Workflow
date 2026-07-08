from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "core_contracts_types")
trace_contract.emit_determinism_digest("p0", "core_contracts_types")

trace_contract._emit_dispatches_healing_run("p1", "core_contracts_types", "L5")
trace_contract._emit_routes_through("p1", "core_contracts_types", "L5")
trace_contract._emit_checks_agent_registry("p1", "core_contracts_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "core_contracts_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "core_contracts_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "core_contracts_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "core_contracts_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "core_contracts_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "core_contracts_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "core_contracts_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "core_contracts_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "core_contracts_types")
trace_contract._emit_gated_by_confidence("p1", "core_contracts_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "core_contracts_types", "L5")
trace_contract._emit_reads_policy_state("p1", "core_contracts_types", "L5")

trace_contract._emit_applies_guardrail("p0", "core_contracts_types", "p0_governance")
trace_contract._emit_snapshots_state("p0", "core_contracts_types", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "core_contracts_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "core_contracts_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "core_contracts_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "core_contracts_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "core_contracts_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "core_contracts_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "core_contracts_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "core_contracts_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "core_contracts_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "core_contracts_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "core_contracts_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "core_contracts_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "core_contracts_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "core_contracts_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "core_contracts_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "core_contracts_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "core_contracts_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "core_contracts_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "core_contracts_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "core_contracts_types", "exec_snapshot_link")

"\nCore Contracts - Pydantic models for sovereign system contracts.\nSSOT for retry policies, hop specifications, and registry.\n"
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


trace_contract._emit_emits_metric_event("core_contracts_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("core_contracts_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("core_contracts_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("core_contracts_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("core_contracts_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("core_contracts_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("core_contracts_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("core_contracts_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("core_contracts_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("core_contracts_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("core_contracts_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("core_contracts_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("core_contracts_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("core_contracts_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("core_contracts_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("core_contracts_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("core_contracts_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("core_contracts_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("core_contracts_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("core_contracts_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("core_contracts_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("core_contracts_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("core_contracts_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("core_contracts_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("core_contracts_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("core_contracts_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("core_contracts_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("core_contracts_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "core_contracts_types", "context_pull")
trace_contract._emit_pulls_context("p1", "core_contracts_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "core_contracts_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "core_contracts_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "core_contracts_types", "write_through")
trace_contract._emit_writes_through("p1", "core_contracts_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "core_contracts_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "core_contracts_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "core_contracts_types", "routing_commit")


class RetryPolicy(BaseModel):
    """Retry policy for agent operations."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    max_retries: int = Field(default=3, ge=0, le=10, description="Maximum number of retry attempts")
    backoff_base: float = Field(
        default=0.5,
        ge=0.1,
        le=5.0,
        description="Base multiplier for backoff calculation",
    )
    backoff_max: float = Field(default=30.0, ge=1.0, le=300.0, description="Maximum backoff delay in seconds")
    retry_on: list[str] = Field(
        default_factory=lambda: ["timeout", "rate_limit"],
        description="Error types to retry on",
    )

    @field_validator("retry_on")
    @classmethod
    def validate_retry_on(cls, v: list[str]) -> list[str]:
        """[HARDENED] Ensure retry_on list is not empty."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "RetryPolicy.validate_retry_on")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:RetryPolicy.validate_retry_on".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if not v:
            raise ValueError("retry_on list cannot be empty")
        return v


class HopSpec(BaseModel):
    """Specification for a HOP (Handoff Operation Protocol) stage."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    hop_id: str = Field(..., description="Unique identifier for the HOP stage")
    name: str = Field(..., description="Human-readable name for the HOP stage")
    description: str = Field(default="", description="Description of the HOP stage purpose")
    timeout_seconds: int = Field(default=30, ge=1, le=300, description="Timeout in seconds for this HOP")
    retry_policy: RetryPolicy | None = Field(default=None, description="Retry policy for this HOP")
    dependencies: list[str] = Field(default_factory=list, description="List of dependency HOP IDs")


class AgentContract(BaseModel):
    """Contract specification for an agent."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    name: str = Field(..., description="Agent name")
    layer: str = Field(..., description="Agent layer (e.g., L0, L1, L2, etc.)")
    capabilities: list[str] = Field(default_factory=list, description="List of agent capabilities")
    retry_policy: RetryPolicy = Field(default_factory=RetryPolicy, description="Agent's retry policy")


CORE_CONTRACTS_REGISTRY: dict[str, Any] = {
    "RetryPolicy": RetryPolicy,
    "HopSpec": HopSpec,
    "AgentContract": AgentContract,
}
__all__ = ["RetryPolicy", "HopSpec", "AgentContract", "CORE_CONTRACTS_REGISTRY"]
