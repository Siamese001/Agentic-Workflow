from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "budget_types")
trace_contract.emit_determinism_digest("p0", "budget_types")

trace_contract._emit_dispatches_healing_run("p1", "budget_types", "L1")
trace_contract._emit_routes_through("p1", "budget_types", "L1")
trace_contract._emit_checks_agent_registry("p1", "budget_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "budget_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "budget_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "budget_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "budget_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "budget_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "budget_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "budget_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "budget_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "budget_types")
trace_contract._emit_gated_by_confidence("p1", "budget_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "budget_types", "L1")
trace_contract._emit_reads_policy_state("p1", "budget_types", "L1")

trace_contract._emit_snapshots_state("p0", "budget_types", "state_snapshot")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_applies_guardrail("p0", "budget_types", "p0_governance")
trace_contract._emit_records_execution_trace("p0", "evidence", "budget_types")
trace_contract._emit_authorize_and_execute("p2", "budget_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "budget_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "budget_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "budget_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "budget_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "budget_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "budget_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "budget_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "budget_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "budget_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "budget_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "budget_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "budget_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "budget_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "budget_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "budget_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "budget_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "budget_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "budget_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "budget_types", "exec_snapshot_link")

"Dataclass models for lic_routing_rules."
import logging
from dataclasses import dataclass, field


trace_contract._emit_emits_metric_event("budget_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("budget_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("budget_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("budget_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("budget_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("budget_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("budget_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("budget_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("budget_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("budget_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("budget_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("budget_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("budget_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("budget_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("budget_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("budget_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("budget_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("budget_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("budget_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("budget_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("budget_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("budget_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("budget_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("budget_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("budget_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("budget_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("budget_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("budget_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "budget_types", "context_pull")
trace_contract._emit_pulls_context("p1", "budget_types", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "budget_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "budget_types", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "budget_types", "write_through")
trace_contract._emit_writes_through("p1", "budget_types", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "budget_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "budget_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "budget_types", "routing_commit")

_logger = logging.getLogger(__name__)


@dataclass
class ToolCallBudget:
    """Tool call budget configuration."""

    _minimum: int = 0
    _maximum: int = 20
    _guidance: dict[str, str] = field(default_factory=dict)
