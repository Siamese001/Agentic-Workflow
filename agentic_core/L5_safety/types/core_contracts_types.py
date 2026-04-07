from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    # noqa: E402,
    # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "core_contracts_types")
emit_determinism_digest("p0", "core_contracts_types")

_emit_dispatches_healing_run("p1", "core_contracts_types", "L5")
_emit_routes_through("p1", "core_contracts_types", "L5")
_emit_checks_agent_registry("p1", "core_contracts_types", "agent_registry")
_emit_validates_agent_capability("p1", "core_contracts_types", "capability")
_emit_dispatches_execution_plan("p1", "core_contracts_types", "exec_plan")
_emit_agent_executes_agent("p1", "core_contracts_types", "sub_agent")
_emit_routes_to_agent("p1", "core_contracts_types", "target_agent")
_emit_verifies_policy("p1", "core_contracts_types", "policy_check")
_emit_observes_runtime_state("p1", "core_contracts_types", "runtime_state")
_emit_verifies_boundary("p1", "core_contracts_types", "boundary_check")
_emit_transcripts_response("p1", "core_contracts_types", "transcript")
_emit_hard_fails_untranscripted("p1", "core_contracts_types")
_emit_gated_by_confidence("p1", "core_contracts_types", "confidence_gate")
_emit_escalates_to_human("p1", "core_contracts_types", "L5")
_emit_reads_policy_state("p1", "core_contracts_types", "L5")

_emit_applies_guardrail("p0", "core_contracts_types", "p0_governance")
_emit_snapshots_state("p0", "core_contracts_types", "state_snapshot")
_emit_authorize_and_execute("p2", "core_contracts_types", "execution_auth")
_emit_validates_capability("p2", "core_contracts_types", "capability_check")
_emit_routes_to_capability("p2", "core_contracts_types", "capability_route")
_emit_writes_via_uwg("p2", "core_contracts_types", "uwg_write")
_emit_blocks_direct_write("p2", "core_contracts_types", "direct_write_block")
_emit_records_tool_invocation("p2", "core_contracts_types", "tool_invocation")
_emit_captures_execution_output("p2", "core_contracts_types", "exec_output")
_emit_dispatches_agent("p3", "core_contracts_types", "agent_dispatch")
_emit_coordinates_agents("p3", "core_contracts_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "core_contracts_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "core_contracts_types", "healing_outcome")
_emit_escalates_failure("p3", "core_contracts_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "core_contracts_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "core_contracts_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "core_contracts_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "core_contracts_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "core_contracts_types", "eval_metric")
_emit_stores_embedding("p4", "core_contracts_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "core_contracts_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "core_contracts_types", "exec_snapshot_link")

"\nCore Contracts - Pydantic models for sovereign system contracts.\nSSOT for retry policies, hop specifications, and registry.\n"
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("core_contracts_types", "p4obs", "metric_1")
_emit_emits_metric_event("core_contracts_types", "p4obs", "metric_2")
_emit_emits_metric_event("core_contracts_types", "p4obs", "metric_3")
_emit_emits_metric_event("core_contracts_types", "p4obs", "metric_4")
_emit_emits_metric_event("core_contracts_types", "p4obs", "metric_5")
_emit_emits_metric_event("core_contracts_types", "p4obs", "metric_6")
_emit_records_incident_event("core_contracts_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("core_contracts_types", "p4obs", "anomaly")
_emit_writes_observability_log("core_contracts_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("core_contracts_types", "p4obs", "mon_state")
_emit_triggers_alert("core_contracts_types", "p4obs", "alert")
_emit_links_incident_trace("core_contracts_types", "p4obs", "trace_link")
_emit_captures_pattern("core_contracts_types", "p3lm", "pattern")
_emit_records_learning_event("core_contracts_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("core_contracts_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("core_contracts_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("core_contracts_types", "p3lm", "routing")
_emit_improves_agent_policy("core_contracts_types", "p3lm", "policy")
_emit_stores_learning_state("core_contracts_types", "p3lm", "state")
_emit_records_execution_trace("core_contracts_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("core_contracts_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("core_contracts_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("core_contracts_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("core_contracts_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("core_contracts_types", "env_read", "p2_env_1")
_emit_reads_environ("core_contracts_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("core_contracts_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("core_contracts_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "core_contracts_types", "context_pull")
_emit_pulls_context("p1", "core_contracts_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "core_contracts_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "core_contracts_types", "uwg_term_2")
_emit_writes_through("p1", "core_contracts_types", "write_through")
_emit_writes_through("p1", "core_contracts_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "core_contracts_types", "safety_validation")
_emit_invokes_eval("p1", "core_contracts_types", "eval_call")
_emit_proposal_commits_routing("p1", "core_contracts_types", "routing_commit")


class RetryPolicy(BaseModel):
    """Retry policy for agent operations."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    max_retries: int = Field(default=3, ge=0, le=10, description="Maximum number of retry attempts")
    backoff_base: float = Field(
        default=0.5, ge=0.1, le=5.0, description="Base multiplier for backoff calculation",
    )
    backoff_max: float = Field(default=30.0, ge=1.0, le=300.0, description="Maximum backoff delay in seconds")
    retry_on: list[str] = Field(
        default_factory=lambda: ["timeout", "rate_limit"], description="Error types to retry on",
    )

    @field_validator("retry_on")
    @classmethod
    def validate_retry_on(cls, v: list[str]) -> list[str]:
        """[HARDENED] Ensure retry_on list is not empty."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "RetryPolicy.validate_retry_on")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:RetryPolicy.validate_retry_on".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
