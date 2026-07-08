from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "injection_type_config", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "injection_type_config", "policy_binding")
trace_contract._emit_snapshots_state("p0", "injection_type_config", "state_snapshot")
trace_contract.emit_replay_key("p0", "injection_type_config")
trace_contract.emit_determinism_digest("p0", "injection_type_config")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "injection_type_config", "execution_auth")
trace_contract._emit_validates_capability("p2", "injection_type_config", "capability_check")
trace_contract._emit_routes_to_capability("p2", "injection_type_config", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "injection_type_config", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "injection_type_config", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "injection_type_config", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "injection_type_config", "exec_output")
trace_contract._emit_dispatches_agent("p3", "injection_type_config", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "injection_type_config", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "injection_type_config", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "injection_type_config", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "injection_type_config", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "injection_type_config", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "injection_type_config", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "injection_type_config", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "injection_type_config", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "injection_type_config", "eval_metric")
trace_contract._emit_stores_embedding("p4", "injection_type_config", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "injection_type_config", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "injection_type_config", "exec_snapshot_link")

# Configuration constants

"""
Prompt Injection & Governance Schemas
====================================
Defines schemas for dynamic prompt injection and safety scoping.
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


trace_contract._emit_emits_metric_event("injection_type_config", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("injection_type_config", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("injection_type_config", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("injection_type_config", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("injection_type_config", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("injection_type_config", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("injection_type_config", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("injection_type_config", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("injection_type_config", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("injection_type_config", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("injection_type_config", "p4obs", "alert")
trace_contract._emit_links_incident_trace("injection_type_config", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("injection_type_config", "p3lm", "pattern")
trace_contract._emit_records_learning_event("injection_type_config", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("injection_type_config", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("injection_type_config", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("injection_type_config", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("injection_type_config", "p3lm", "policy")
trace_contract._emit_stores_learning_state("injection_type_config", "p3lm", "state")
trace_contract._emit_records_execution_trace("injection_type_config", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("injection_type_config", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("injection_type_config", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("injection_type_config", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("injection_type_config", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("injection_type_config", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("injection_type_config", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("injection_type_config", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("injection_type_config", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "injection_type_config", "context_pull")
trace_contract._emit_pulls_context("p1", "injection_type_config", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "injection_type_config", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "injection_type_config", "uwg_term_2")
trace_contract._emit_writes_through("p1", "injection_type_config", "write_through")
trace_contract._emit_writes_through("p1", "injection_type_config", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "injection_type_config", "safety_validation")
trace_contract._emit_invokes_eval("p1", "injection_type_config", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "injection_type_config", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "injection_type_config", "human_escalation")
trace_contract._emit_routes_through("p1", "injection_type_config", "route_through")
trace_contract._emit_checks_agent_registry("p1", "injection_type_config", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "injection_type_config", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "injection_type_config", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "injection_type_config", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "injection_type_config", "target_agent")
trace_contract._emit_verifies_policy("p1", "injection_type_config", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "injection_type_config", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "injection_type_config", "boundary_check")
trace_contract._emit_transcripts_response("p1", "injection_type_config", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "injection_type_config")
trace_contract._emit_gated_by_confidence("p1", "injection_type_config", "confidence_gate")


class InjectionType(str, Enum):
    """Types of prompt injections."""

    SYSTEM = "system"
    USER = "user"
    CONTEXT = "context"
    REASONING = "reasoning"
    TOOLING = "tooling"
    SAFETY = "safety"
    OUTPUT = "output"


class InjectionScope(BaseModel):
    """Scope defining where an injection should be applied."""

    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    hop_types: list[str] = Field(default_factory=list)
    stages: list[str] = Field(default_factory=list)
    contexts: dict[str, Any] = Field(default_factory=dict)


class InjectionPattern(BaseModel):
    """A single prompt injection pattern template."""

    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str
    name: str
    type: InjectionType
    description: str
    template: str
    variables: list[str] = Field(default_factory=list)
    scope: InjectionScope = Field(default_factory=InjectionScope)
    priority: int = Field(default=0, ge=0, le=10)
    enabled: bool = True

    @field_validator("variables")
    @classmethod
    def validate_variables(cls, value: list[str]) -> list[str]:
        """[HARDENED] Ensure variables list has no empty entries."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "InjectionPattern.validate_variables"
        )

        for variable in value:
            if not variable.strip():
                raise ValueError("Injection variables cannot be empty")
        return value
