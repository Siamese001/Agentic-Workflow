"""
agentic_core/L1_cognition/reasoning/types/observability_types.py

Passive data structures for MetaLearningObservability.
Extracted from engine/meta_observability.py to prevent circular dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.record_execution_trace("observability_types", "observability_types_trace")


trace_contract._emit_emits_metric_event("observability_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("observability_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("observability_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("observability_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("observability_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("observability_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("observability_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("observability_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("observability_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("observability_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("observability_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("observability_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("observability_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("observability_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("observability_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("observability_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("observability_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("observability_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("observability_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("observability_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("observability_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("observability_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("observability_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("observability_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("observability_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("observability_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("observability_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("observability_types", "runtime_state", "p2_rt_2")

trace_contract.emit_replay_key("p0", "observability_types")
trace_contract.emit_determinism_digest("p0", "observability_types")

trace_contract._emit_dispatches_healing_run("p1", "observability_types", "L1")
trace_contract._emit_routes_through("p1", "observability_types", "L1")
trace_contract._emit_checks_agent_registry("p1", "observability_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "observability_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "observability_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "observability_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "observability_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "observability_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "observability_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "observability_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "observability_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "observability_types")
trace_contract._emit_gated_by_confidence("p1", "observability_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "observability_types", "L1")
trace_contract._emit_reads_policy_state("p1", "observability_types", "L1")
trace_contract._emit_pulls_context("p1", "observability_types", "context_pull")
trace_contract._emit_pulls_context("p1", "observability_types", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "observability_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "observability_types", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "observability_types", "write_through")
trace_contract._emit_writes_through("p1", "observability_types", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "observability_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "observability_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "observability_types", "routing_commit")

trace_contract._emit_snapshots_state("p0", "observability_types", "state_snapshot")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_applies_guardrail("p0", "observability_types", "p0_governance")
trace_contract._emit_records_execution_trace("p0", "evidence", "observability_types")
trace_contract._emit_authorize_and_execute("p2", "observability_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "observability_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "observability_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "observability_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "observability_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "observability_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "observability_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "observability_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "observability_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "observability_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "observability_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "observability_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "observability_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "observability_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "observability_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "observability_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "observability_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "observability_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "observability_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "observability_types", "exec_snapshot_link")


@dataclass
class MetricPoint:
    """A single metric data point."""

    name: str
    value: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: dict[str, str] = field(default_factory=dict)


@dataclass
class HealthStatus:
    """Health status for a component."""

    component: str
    healthy: bool
    message: str
    last_check: str = field(default_factory=lambda: datetime.now().isoformat())
    details: dict[str, Any] = field(default_factory=dict)
