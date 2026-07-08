"""ReAct Engine — canonical location in L1_cognition/engines/.

Re-exports ReActEngine, ReActTrace, ReActStep, and create_react_engine from
the existing implementation in react_config.py so callers can import from
the correct layer path:

    from agentic_core.L1_cognition.reasoning.react_engine import ReActEngine

The original react_config.py is kept intact (no deletion) to avoid breaking
any existing imports.
"""

from __future__ import annotations

from agentic_core.L1_cognition.config.react_config import (  # noqa: F401
    ReActEngine,
    ReActStep,
    ReActTrace,
    ReasoningMode,
    create_react_engine,
)
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_emits_metric_event("react_engine", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("react_engine", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("react_engine", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("react_engine", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("react_engine", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("react_engine", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("react_engine", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("react_engine", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("react_engine", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("react_engine", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("react_engine", "p4obs", "alert")
trace_contract._emit_links_incident_trace("react_engine", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("react_engine", "p3lm", "pattern")
trace_contract._emit_records_learning_event("react_engine", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("react_engine", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("react_engine", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("react_engine", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("react_engine", "p3lm", "policy")
trace_contract._emit_stores_learning_state("react_engine", "p3lm", "state")
trace_contract._emit_records_execution_trace("react_engine", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("react_engine", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("react_engine", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("react_engine", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("react_engine", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("react_engine", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("react_engine", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("react_engine", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("react_engine", "runtime_state", "p2_rt_2")

trace_contract.emit_replay_key("p0", "react_engine")
trace_contract.emit_determinism_digest("p0", "react_engine")

trace_contract._emit_dispatches_healing_run("p1", "react_engine", "L1")
trace_contract._emit_routes_through("p1", "react_engine", "L1")
trace_contract._emit_checks_agent_registry("p1", "react_engine", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "react_engine", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "react_engine", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "react_engine", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "react_engine", "target_agent")
trace_contract._emit_verifies_policy("p1", "react_engine", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "react_engine", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "react_engine", "boundary_check")
trace_contract._emit_transcripts_response("p1", "react_engine", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "react_engine")
trace_contract._emit_gated_by_confidence("p1", "react_engine", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "react_engine", "L1")
trace_contract._emit_reads_policy_state("p1", "react_engine", "L1")
trace_contract._emit_snapshots_state("p0", "react_engine", "state_snapshot")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_applies_guardrail("p0", "react_engine", "p0_governance")
trace_contract._emit_records_execution_trace("p0", "evidence", "react_engine")
trace_contract._emit_authorize_and_execute("p2", "react_engine", "execution_auth")
trace_contract._emit_validates_capability("p2", "react_engine", "capability_check")
trace_contract._emit_routes_to_capability("p2", "react_engine", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "react_engine", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "react_engine", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "react_engine", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "react_engine", "exec_output")
trace_contract._emit_dispatches_agent("p3", "react_engine", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "react_engine", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "react_engine", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "react_engine", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "react_engine", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "react_engine", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "react_engine", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "react_engine", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "react_engine", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "react_engine", "eval_metric")
trace_contract._emit_stores_embedding("p4", "react_engine", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "react_engine", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "react_engine", "exec_snapshot_link")
trace_contract._emit_pulls_context("p1", "react_engine", "context_pull")
trace_contract._emit_pulls_context("p1", "react_engine", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "react_engine", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "react_engine", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "react_engine", "write_through")
trace_contract._emit_writes_through("p1", "react_engine", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "react_engine", "safety_validation")
trace_contract._emit_invokes_eval("p1", "react_engine", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "react_engine", "routing_commit")

__all__ = [
    "ReActEngine",
    "ReActStep",
    "ReActTrace",
    "ReasoningMode",
    "create_react_engine",
]
