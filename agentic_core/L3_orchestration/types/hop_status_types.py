from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "hop_status_types")
emit_determinism_digest("p0", "hop_status_types")

_emit_dispatches_healing_run("p1", "hop_status_types", "L3")
_emit_routes_through("p1", "hop_status_types", "L3")
_emit_checks_agent_registry("p1", "hop_status_types", "agent_registry")
_emit_validates_agent_capability("p1", "hop_status_types", "capability")
_emit_dispatches_execution_plan("p1", "hop_status_types", "exec_plan")
_emit_agent_executes_agent("p1", "hop_status_types", "sub_agent")
_emit_routes_to_agent("p1", "hop_status_types", "target_agent")
_emit_verifies_policy("p1", "hop_status_types", "policy_check")
_emit_observes_runtime_state("p1", "hop_status_types", "runtime_state")
_emit_verifies_boundary("p1", "hop_status_types", "boundary_check")
_emit_transcripts_response("p1", "hop_status_types", "transcript")
_emit_hard_fails_untranscripted("p1", "hop_status_types")
_emit_gated_by_confidence("p1", "hop_status_types", "confidence_gate")
_emit_escalates_to_human("p1", "hop_status_types", "L3")
_emit_reads_policy_state("p1", "hop_status_types", "L3")

_emit_snapshots_state("p0", "hop_status_types", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "hop_status_types", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "hop_status_types")
_emit_authorize_and_execute("p2", "hop_status_types", "execution_auth")
_emit_validates_capability("p2", "hop_status_types", "capability_check")
_emit_routes_to_capability("p2", "hop_status_types", "capability_route")
_emit_writes_via_uwg("p2", "hop_status_types", "uwg_write")
_emit_blocks_direct_write("p2", "hop_status_types", "direct_write_block")
_emit_records_tool_invocation("p2", "hop_status_types", "tool_invocation")
_emit_captures_execution_output("p2", "hop_status_types", "exec_output")
_emit_dispatches_agent("p3", "hop_status_types", "agent_dispatch")
_emit_coordinates_agents("p3", "hop_status_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "hop_status_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "hop_status_types", "healing_outcome")
_emit_escalates_failure("p3", "hop_status_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "hop_status_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "hop_status_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "hop_status_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "hop_status_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "hop_status_types", "eval_metric")
_emit_stores_embedding("p4", "hop_status_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "hop_status_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "hop_status_types", "exec_snapshot_link")

"Enum types for orchestrate_workflow_types."
import logging
from enum import Enum

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("hop_status_types", "p4obs", "metric_1")
_emit_emits_metric_event("hop_status_types", "p4obs", "metric_2")
_emit_emits_metric_event("hop_status_types", "p4obs", "metric_3")
_emit_emits_metric_event("hop_status_types", "p4obs", "metric_4")
_emit_emits_metric_event("hop_status_types", "p4obs", "metric_5")
_emit_emits_metric_event("hop_status_types", "p4obs", "metric_6")
_emit_records_incident_event("hop_status_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("hop_status_types", "p4obs", "anomaly")
_emit_writes_observability_log("hop_status_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("hop_status_types", "p4obs", "mon_state")
_emit_triggers_alert("hop_status_types", "p4obs", "alert")
_emit_links_incident_trace("hop_status_types", "p4obs", "trace_link")
_emit_captures_pattern("hop_status_types", "p3lm", "pattern")
_emit_records_learning_event("hop_status_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("hop_status_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("hop_status_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("hop_status_types", "p3lm", "routing")
_emit_improves_agent_policy("hop_status_types", "p3lm", "policy")
_emit_stores_learning_state("hop_status_types", "p3lm", "state")
_emit_records_execution_trace("hop_status_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("hop_status_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("hop_status_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("hop_status_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("hop_status_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("hop_status_types", "env_read", "p2_env_1")
_emit_reads_environ("hop_status_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("hop_status_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("hop_status_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "hop_status_types", "context_pull")
_emit_pulls_context("p1", "hop_status_types", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "hop_status_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "hop_status_types", "uwg_term_secondary")
_emit_writes_through("p1", "hop_status_types", "write_through")
_emit_writes_through("p1", "hop_status_types", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "hop_status_types", "safety_validation")
_emit_invokes_eval("p1", "hop_status_types", "eval_call")
_emit_proposal_commits_routing("p1", "hop_status_types", "routing_commit")

_logger = logging.getLogger(__name__)


class HopStatus(Enum):
    """Status of a workflow hop."""


class GateDecision(Enum):
    """Decision from a validation gate."""
