"""
agentic_core/L1_cognition/reasoning/types/observability_types.py

Passive data structures for MetaLearningObservability.
Extracted from engine/meta_observability.py to prevent circular dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    record_execution_trace,
)

record_execution_trace("observability_types", "observability_types_trace")


_emit_emits_metric_event("observability_types", "p4obs", "metric_1")
_emit_emits_metric_event("observability_types", "p4obs", "metric_2")
_emit_emits_metric_event("observability_types", "p4obs", "metric_3")
_emit_emits_metric_event("observability_types", "p4obs", "metric_4")
_emit_emits_metric_event("observability_types", "p4obs", "metric_5")
_emit_emits_metric_event("observability_types", "p4obs", "metric_6")
_emit_records_incident_event("observability_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("observability_types", "p4obs", "anomaly")
_emit_writes_observability_log("observability_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("observability_types", "p4obs", "mon_state")
_emit_triggers_alert("observability_types", "p4obs", "alert")
_emit_links_incident_trace("observability_types", "p4obs", "trace_link")
_emit_captures_pattern("observability_types", "p3lm", "pattern")
_emit_records_learning_event("observability_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("observability_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("observability_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("observability_types", "p3lm", "routing")
_emit_improves_agent_policy("observability_types", "p3lm", "policy")
_emit_stores_learning_state("observability_types", "p3lm", "state")
_emit_records_execution_trace("observability_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("observability_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("observability_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("observability_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("observability_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("observability_types", "env_read", "p2_env_1")
_emit_reads_environ("observability_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("observability_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("observability_types", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "observability_types")
emit_determinism_digest("p0", "observability_types")

_emit_dispatches_healing_run("p1", "observability_types", "L1")
_emit_routes_through("p1", "observability_types", "L1")
_emit_checks_agent_registry("p1", "observability_types", "agent_registry")
_emit_validates_agent_capability("p1", "observability_types", "capability")
_emit_dispatches_execution_plan("p1", "observability_types", "exec_plan")
_emit_agent_executes_agent("p1", "observability_types", "sub_agent")
_emit_routes_to_agent("p1", "observability_types", "target_agent")
_emit_verifies_policy("p1", "observability_types", "policy_check")
_emit_observes_runtime_state("p1", "observability_types", "runtime_state")
_emit_verifies_boundary("p1", "observability_types", "boundary_check")
_emit_transcripts_response("p1", "observability_types", "transcript")
_emit_hard_fails_untranscripted("p1", "observability_types")
_emit_gated_by_confidence("p1", "observability_types", "confidence_gate")
_emit_escalates_to_human("p1", "observability_types", "L1")
_emit_reads_policy_state("p1", "observability_types", "L1")
_emit_pulls_context("p1", "observability_types", "context_pull")
_emit_pulls_context("p1", "observability_types", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "observability_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "observability_types", "uwg_term_secondary")
_emit_writes_through("p1", "observability_types", "write_through")
_emit_writes_through("p1", "observability_types", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "observability_types", "safety_validation")
_emit_invokes_eval("p1", "observability_types", "eval_call")
_emit_proposal_commits_routing("p1", "observability_types", "routing_commit")

_emit_snapshots_state("p0", "observability_types", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "observability_types", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "observability_types")
_emit_authorize_and_execute("p2", "observability_types", "execution_auth")
_emit_validates_capability("p2", "observability_types", "capability_check")
_emit_routes_to_capability("p2", "observability_types", "capability_route")
_emit_writes_via_uwg("p2", "observability_types", "uwg_write")
_emit_blocks_direct_write("p2", "observability_types", "direct_write_block")
_emit_records_tool_invocation("p2", "observability_types", "tool_invocation")
_emit_captures_execution_output("p2", "observability_types", "exec_output")
_emit_dispatches_agent("p3", "observability_types", "agent_dispatch")
_emit_coordinates_agents("p3", "observability_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "observability_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "observability_types", "healing_outcome")
_emit_escalates_failure("p3", "observability_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "observability_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "observability_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "observability_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "observability_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "observability_types", "eval_metric")
_emit_stores_embedding("p4", "observability_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "observability_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "observability_types", "exec_snapshot_link")


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
