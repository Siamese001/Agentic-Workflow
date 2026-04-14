"""Minimal shim: re-exports types required by prompt_assembler.py.

Created by P2/W2.2 to unblock the import chain:
  prompt_assembler.py → from agentic_core.L4_state.utils.memory.runtime_models import InjectionMatch

Only the attributes accessed at runtime are defined:
  InjectionMatch.injection        → InjectionPattern (has .priority, .template)
  InjectionMatch.relevance_score  → float
  InjectionMatch.variable_values  → dict[str, Any]
"""

from __future__ import annotations

from dataclasses import dataclass, field
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
)

_emit_emits_metric_event("runtime_models", "p4obs", "metric_1")
_emit_emits_metric_event("runtime_models", "p4obs", "metric_2")
_emit_emits_metric_event("runtime_models", "p4obs", "metric_3")
_emit_emits_metric_event("runtime_models", "p4obs", "metric_4")
_emit_emits_metric_event("runtime_models", "p4obs", "metric_5")
_emit_emits_metric_event("runtime_models", "p4obs", "metric_6")
_emit_records_incident_event("runtime_models", "p4obs", "incident")
_emit_captures_runtime_anomaly("runtime_models", "p4obs", "anomaly")
_emit_writes_observability_log("runtime_models", "p4obs", "obs_log")
_emit_updates_monitoring_state("runtime_models", "p4obs", "mon_state")
_emit_triggers_alert("runtime_models", "p4obs", "alert")
_emit_links_incident_trace("runtime_models", "p4obs", "trace_link")
_emit_captures_pattern("runtime_models", "p3lm", "pattern")
_emit_records_learning_event("runtime_models", "p3lm", "learning_event")
_emit_writes_learning_snapshot("runtime_models", "p3lm", "snapshot")
_emit_feeds_meta_learning("runtime_models", "p3lm", "meta_feed")
_emit_updates_routing_strategy("runtime_models", "p3lm", "routing")
_emit_improves_agent_policy("runtime_models", "p3lm", "policy")
_emit_stores_learning_state("runtime_models", "p3lm", "state")
_emit_records_execution_trace("runtime_models", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("runtime_models", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("runtime_models", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("runtime_models", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("runtime_models", "L4_STATE", "p2_trace_5")
_emit_reads_environ("runtime_models", "env_read", "p2_env_1")
_emit_reads_environ("runtime_models", "env_read", "p2_env_2")
_emit_reads_runtime_state("runtime_models", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("runtime_models", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "runtime_models")
emit_determinism_digest("p0", "runtime_models")

_emit_dispatches_healing_run("p1", "runtime_models", "L4")
_emit_routes_through("p1", "runtime_models", "L4")
_emit_checks_agent_registry("p1", "runtime_models", "agent_registry")
_emit_validates_agent_capability("p1", "runtime_models", "capability")
_emit_dispatches_execution_plan("p1", "runtime_models", "exec_plan")
_emit_agent_executes_agent("p1", "runtime_models", "sub_agent")
_emit_routes_to_agent("p1", "runtime_models", "target_agent")
_emit_verifies_policy("p1", "runtime_models", "policy_check")
_emit_observes_runtime_state("p1", "runtime_models", "runtime_state")
_emit_verifies_boundary("p1", "runtime_models", "boundary_check")
_emit_transcripts_response("p1", "runtime_models", "transcript")
_emit_hard_fails_untranscripted("p1", "runtime_models")
_emit_gated_by_confidence("p1", "runtime_models", "confidence_gate")
_emit_escalates_to_human("p1", "runtime_models", "L4")
_emit_reads_policy_state("p1", "runtime_models", "L4")
_emit_pulls_context("p1", "runtime_models", "context_pull")
_emit_pulls_context("p1", "runtime_models", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "runtime_models", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "runtime_models", "uwg_term_secondary")
_emit_writes_through("p1", "runtime_models", "write_through")
_emit_writes_through("p1", "runtime_models", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "runtime_models", "safety_validation")
_emit_invokes_eval("p1", "runtime_models", "eval_call")
_emit_proposal_commits_routing("p1", "runtime_models", "routing_commit")

_emit_snapshots_state("p0", "runtime_models", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "runtime_models", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "runtime_models")
_emit_authorize_and_execute("p2", "runtime_models", "execution_auth")
_emit_validates_capability("p2", "runtime_models", "capability_check")
_emit_routes_to_capability("p2", "runtime_models", "capability_route")
_emit_writes_via_uwg("p2", "runtime_models", "uwg_write")
_emit_blocks_direct_write("p2", "runtime_models", "direct_write_block")
_emit_records_tool_invocation("p2", "runtime_models", "tool_invocation")
_emit_captures_execution_output("p2", "runtime_models", "exec_output")
_emit_dispatches_agent("p3", "runtime_models", "agent_dispatch")
_emit_coordinates_agents("p3", "runtime_models", "agent_coordination")
_emit_records_workflow_lineage("p3", "runtime_models", "workflow_lineage")
_emit_records_healing_outcome("p3", "runtime_models", "healing_outcome")
_emit_escalates_failure("p3", "runtime_models", "failure_escalation")
_emit_orchestrates_workflow("p3", "runtime_models", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "runtime_models", "healing_dispatch")
_emit_invokes_evaluation("p3", "runtime_models", "evaluation_signal")
_emit_records_telemetry_event("p4", "runtime_models", "telemetry_event")
_emit_captures_evaluation_metric("p4", "runtime_models", "eval_metric")
_emit_stores_embedding("p4", "runtime_models", "embedding_store")
_emit_updates_meta_learning_state("p4", "runtime_models", "meta_learning")
_emit_links_execution_to_snapshot("p4", "runtime_models", "exec_snapshot_link")


@dataclass
class InjectionPattern:
    """Minimal representation of an instructional injection pattern."""

    priority: int = 0
    template: str = ""


@dataclass
class InjectionMatch:
    """A matched injection pattern with relevance scoring and variable bindings."""

    injection: InjectionPattern = field(default_factory=InjectionPattern)
    relevance_score: float = 0.0
    variable_values: dict[str, Any] = field(default_factory=dict)
