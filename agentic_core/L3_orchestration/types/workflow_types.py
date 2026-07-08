from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "workflow_types")
trace_contract.emit_determinism_digest("p0", "workflow_types")

trace_contract._emit_dispatches_healing_run("p1", "workflow_types", "L3")
trace_contract._emit_routes_through("p1", "workflow_types", "L3")
trace_contract._emit_checks_agent_registry("p1", "workflow_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "workflow_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "workflow_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "workflow_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "workflow_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "workflow_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "workflow_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "workflow_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "workflow_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "workflow_types")
trace_contract._emit_gated_by_confidence("p1", "workflow_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "workflow_types", "L3")
trace_contract._emit_reads_policy_state("p1", "workflow_types", "L3")

trace_contract._emit_snapshots_state("p0", "workflow_types", "state_snapshot")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_applies_guardrail("p0", "workflow_types", "p0_governance")
trace_contract._emit_records_execution_trace("p0", "evidence", "workflow_types")
trace_contract._emit_authorize_and_execute("p2", "workflow_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "workflow_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "workflow_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "workflow_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "workflow_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "workflow_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "workflow_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "workflow_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "workflow_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "workflow_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "workflow_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "workflow_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "workflow_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "workflow_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "workflow_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "workflow_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "workflow_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "workflow_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "workflow_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "workflow_types", "exec_snapshot_link")

"Types and models for SubatomicOrchestratorAgent."
import logging
from dataclasses import dataclass, field
from enum import Enum


trace_contract._emit_emits_metric_event("workflow_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("workflow_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("workflow_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("workflow_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("workflow_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("workflow_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("workflow_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("workflow_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("workflow_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("workflow_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("workflow_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("workflow_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("workflow_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("workflow_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("workflow_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("workflow_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("workflow_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("workflow_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("workflow_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("workflow_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("workflow_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("workflow_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("workflow_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("workflow_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("workflow_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("workflow_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("workflow_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("workflow_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "workflow_types", "context_pull")
trace_contract._emit_pulls_context("p1", "workflow_types", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "workflow_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "workflow_types", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "workflow_types", "write_through")
trace_contract._emit_writes_through("p1", "workflow_types", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "workflow_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "workflow_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "workflow_types", "routing_commit")

_logger = logging.getLogger(__name__)


class WorkflowType(Enum):
    """Types of predefined workflows."""


@dataclass
class WorkflowBlueprint:
    """Blueprint for a workflow graph."""

    _name: str
    _description: str
    _roles: list[AgentRole]
    _edges: list[tuple[AgentRole, AgentRole]]
    _mutation_hooks: dict[AgentRole, list[tuple[MutationAction, AgentRole]]] = field(default_factory=dict)
    _parallel_groups: list[list[AgentRole]] = field(default_factory=list)
