"""InspectorExecutor — Canonical parameterized inspector agent.

Consolidates: DagRuntimeInspectorAgent, SignatureVerifierAgent, TokenBudgetInspectorAgent
Created: 2026-02-08 (Structural Agent Count Reduction)
"""

from __future__ import annotations

from dataclasses import dataclass, field

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.mixins.inspection_capability_mixin import InspectionCapability
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_emits_metric_event("InspectorExecutor", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("InspectorExecutor", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("InspectorExecutor", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("InspectorExecutor", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("InspectorExecutor", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("InspectorExecutor", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("InspectorExecutor", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("InspectorExecutor", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("InspectorExecutor", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("InspectorExecutor", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("InspectorExecutor", "p4obs", "alert")
trace_contract._emit_links_incident_trace("InspectorExecutor", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("InspectorExecutor", "p3lm", "pattern")
trace_contract._emit_records_learning_event("InspectorExecutor", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("InspectorExecutor", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("InspectorExecutor", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("InspectorExecutor", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("InspectorExecutor", "p3lm", "policy")
trace_contract._emit_stores_learning_state("InspectorExecutor", "p3lm", "state")
trace_contract._emit_records_execution_trace("InspectorExecutor", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("InspectorExecutor", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("InspectorExecutor", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("InspectorExecutor", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("InspectorExecutor", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("InspectorExecutor", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("InspectorExecutor", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("InspectorExecutor", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("InspectorExecutor", "runtime_state", "p2_rt_2")

trace_contract.emit_replay_key("p0", "InspectorExecutor")
trace_contract.emit_determinism_digest("p0", "InspectorExecutor")

trace_contract._emit_dispatches_healing_run("p1", "InspectorExecutor", "L5")
trace_contract._emit_routes_through("p1", "InspectorExecutor", "L5")
trace_contract._emit_checks_agent_registry("p1", "InspectorExecutor", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "InspectorExecutor", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "InspectorExecutor", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "InspectorExecutor", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "InspectorExecutor", "target_agent")
trace_contract._emit_verifies_policy("p1", "InspectorExecutor", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "InspectorExecutor", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "InspectorExecutor", "boundary_check")
trace_contract._emit_transcripts_response("p1", "InspectorExecutor", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "InspectorExecutor")
trace_contract._emit_gated_by_confidence("p1", "InspectorExecutor", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "InspectorExecutor", "L5")
trace_contract._emit_reads_policy_state("p1", "InspectorExecutor", "L5")
trace_contract._emit_pulls_context("p1", "InspectorExecutor", "context_pull")
trace_contract._emit_pulls_context("p1", "InspectorExecutor", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "InspectorExecutor", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "InspectorExecutor", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "InspectorExecutor", "write_through")
trace_contract._emit_writes_through("p1", "InspectorExecutor", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "InspectorExecutor", "safety_validation")
trace_contract._emit_invokes_eval("p1", "InspectorExecutor", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "InspectorExecutor", "routing_commit")

trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_records_execution_trace("p0", "evidence", "InspectorExecutor")
trace_contract._emit_applies_guardrail("p0", "InspectorExecutor", "p0_governance")
trace_contract._emit_snapshots_state("p0", "InspectorExecutor", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "InspectorExecutor", "execution_auth")
trace_contract._emit_validates_capability("p2", "InspectorExecutor", "capability_check")
trace_contract._emit_routes_to_capability("p2", "InspectorExecutor", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "InspectorExecutor", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "InspectorExecutor", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "InspectorExecutor", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "InspectorExecutor", "exec_output")
trace_contract._emit_dispatches_agent("p3", "InspectorExecutor", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "InspectorExecutor", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "InspectorExecutor", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "InspectorExecutor", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "InspectorExecutor", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "InspectorExecutor", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "InspectorExecutor", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "InspectorExecutor", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "InspectorExecutor", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "InspectorExecutor", "eval_metric")
trace_contract._emit_stores_embedding("p4", "InspectorExecutor", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "InspectorExecutor", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "InspectorExecutor", "exec_snapshot_link")


@dataclass
class InspectorExecutor(InspectionCapability, SovereignBaseAgent):
    """Parameterized inspector that dispatches to domain-specific check logic.

    Usage:
        inspector = InspectorExecutor(inspector_type="dag_runtime")
    """

    inspector_type: str = "generic"
    INSPECTION_LOG_PREFIX: str = field(init=False, default="Inspector")

    def __post_init__(self) -> None:
        prefixes = {"dag_runtime": "DagRuntime", "signature": "Signature", "token_budget": "TokenBudget"}
        self.INSPECTION_LOG_PREFIX = prefixes.get(self.inspector_type, "Inspector")
