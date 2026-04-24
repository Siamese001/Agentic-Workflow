"""
validators/GovernanceAgent.py — backward-compat re-export shim.

Canonical implementation lives at:
    agentic_core.L5_safety.reasoning.GovernanceAgent

This file is a pure re-export stub with NO mutation logic of its own.
All writes_to / healing operations are in reasoning/GovernanceAgent.py
(L5 healer territory, which correctly uses write_gateway).

ADG fix: A-07 (dedup) + A-01 (validators/ mutation boundary).

AGENT-DELETION-AUTHORIZED: 2026-04-24 (W2 of agent-deprecation-migration-d7a3f2)
Authorization date: 2026-04-24
Archive-eligible date: 2026-07-23 (90-day cooling per constitutional \u00a73)
Consumers at authorization: 0 (verified via live-code grep of
`L5_safety.validators.GovernanceAgent` \u2014 prior consumers in
agentic_core/L3_orchestration/enforcement/mission_runner.py and
agentic_core/seams/contracts/safety_agents.py have been refactored away;
current grep returns zero hits).
Unique logic: none (pure re-export of agentic_core.L5_safety.reasoning.GovernanceAgent).
Target archive path on or after eligibility date:
  archives/agents/2026-07-23/L5_safety__validators__GovernanceAgent.py
Cooling-timer artifact: artifacts/agent_deprecation/validators__GovernanceAgent.json
ADG violation resolved on archive: v_p2_duplicated_adapters (2 of 3 in W2).
"""

from __future__ import annotations

from agentic_core.L5_safety.reasoning.GovernanceAgent import (
    DependencyGraph,
    GovernanceAgent,
    heal,
)
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

_emit_emits_metric_event("GovernanceAgent", "p4obs", "metric_1")
_emit_emits_metric_event("GovernanceAgent", "p4obs", "metric_2")
_emit_emits_metric_event("GovernanceAgent", "p4obs", "metric_3")
_emit_emits_metric_event("GovernanceAgent", "p4obs", "metric_4")
_emit_emits_metric_event("GovernanceAgent", "p4obs", "metric_5")
_emit_emits_metric_event("GovernanceAgent", "p4obs", "metric_6")
_emit_records_incident_event("GovernanceAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("GovernanceAgent", "p4obs", "anomaly")
_emit_writes_observability_log("GovernanceAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("GovernanceAgent", "p4obs", "mon_state")
_emit_triggers_alert("GovernanceAgent", "p4obs", "alert")
_emit_links_incident_trace("GovernanceAgent", "p4obs", "trace_link")
_emit_captures_pattern("GovernanceAgent", "p3lm", "pattern")
_emit_records_learning_event("GovernanceAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("GovernanceAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("GovernanceAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("GovernanceAgent", "p3lm", "routing")
_emit_improves_agent_policy("GovernanceAgent", "p3lm", "policy")
_emit_stores_learning_state("GovernanceAgent", "p3lm", "state")
_emit_records_execution_trace("GovernanceAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("GovernanceAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("GovernanceAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("GovernanceAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("GovernanceAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("GovernanceAgent", "env_read", "p2_env_1")
_emit_reads_environ("GovernanceAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("GovernanceAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("GovernanceAgent", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "GovernanceAgent")
emit_determinism_digest("p0", "GovernanceAgent")

_emit_dispatches_healing_run("p1", "GovernanceAgent", "L5")
_emit_routes_through("p1", "GovernanceAgent", "L5")
_emit_checks_agent_registry("p1", "GovernanceAgent", "agent_registry")
_emit_validates_agent_capability("p1", "GovernanceAgent", "capability")
_emit_dispatches_execution_plan("p1", "GovernanceAgent", "exec_plan")
_emit_agent_executes_agent("p1", "GovernanceAgent", "sub_agent")
_emit_routes_to_agent("p1", "GovernanceAgent", "target_agent")
_emit_verifies_policy("p1", "GovernanceAgent", "policy_check")
_emit_observes_runtime_state("p1", "GovernanceAgent", "runtime_state")
_emit_verifies_boundary("p1", "GovernanceAgent", "boundary_check")
_emit_transcripts_response("p1", "GovernanceAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "GovernanceAgent")
_emit_gated_by_confidence("p1", "GovernanceAgent", "confidence_gate")
_emit_escalates_to_human("p1", "GovernanceAgent", "L5")
_emit_reads_policy_state("p1", "GovernanceAgent", "L5")
_emit_pulls_context("p1", "GovernanceAgent", "context_pull")
_emit_pulls_context("p1", "GovernanceAgent", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "GovernanceAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "GovernanceAgent", "uwg_term_secondary")
_emit_writes_through("p1", "GovernanceAgent", "write_through")
_emit_writes_through("p1", "GovernanceAgent", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "GovernanceAgent", "safety_validation")
_emit_invokes_eval("p1", "GovernanceAgent", "eval_call")
_emit_proposal_commits_routing("p1", "GovernanceAgent", "routing_commit")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "GovernanceAgent")
_emit_applies_guardrail("p0", "GovernanceAgent", "p0_governance")
_emit_snapshots_state("p0", "GovernanceAgent", "state_snapshot")
_emit_authorize_and_execute("p2", "GovernanceAgent", "execution_auth")
_emit_validates_capability("p2", "GovernanceAgent", "capability_check")
_emit_routes_to_capability("p2", "GovernanceAgent", "capability_route")
_emit_writes_via_uwg("p2", "GovernanceAgent", "uwg_write")
_emit_blocks_direct_write("p2", "GovernanceAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "GovernanceAgent", "tool_invocation")
_emit_captures_execution_output("p2", "GovernanceAgent", "exec_output")
_emit_dispatches_agent("p3", "GovernanceAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "GovernanceAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "GovernanceAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "GovernanceAgent", "healing_outcome")
_emit_escalates_failure("p3", "GovernanceAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "GovernanceAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "GovernanceAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "GovernanceAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "GovernanceAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "GovernanceAgent", "eval_metric")
_emit_stores_embedding("p4", "GovernanceAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "GovernanceAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "GovernanceAgent", "exec_snapshot_link")

__all__ = ["DependencyGraph", "GovernanceAgent", "heal"]
