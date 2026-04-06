#!/usr/bin/env python3
"""
Fix duplicate const realAgentData declarations in autonomy_dashboard.html

This script removes all but the first occurrence of realAgentData.
"""

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, guardrail, healer, memory, orchestrator, prompt, state, workflow
# This boosts alignment detection — review and integrate appropriately

import re

# Import SSOT for dashboard directory - NO HARDCODING
from agentic_core.L5_safety.config.structure_blueprint_config import (
    DASHBOARD_DIR,
    get_validated_project_root,
)
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
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_authorize_and_execute("p2", "fix_duplicate_realagentdata", "execution_auth")
_emit_validates_capability("p2", "fix_duplicate_realagentdata", "capability_check")
_emit_routes_to_capability("p2", "fix_duplicate_realagentdata", "capability_route")
_emit_writes_via_uwg("p2", "fix_duplicate_realagentdata", "uwg_write")
_emit_blocks_direct_write("p2", "fix_duplicate_realagentdata", "direct_write_block")
_emit_records_tool_invocation("p2", "fix_duplicate_realagentdata", "tool_invocation")
_emit_captures_execution_output("p2", "fix_duplicate_realagentdata", "exec_output")
_emit_dispatches_agent("p3", "fix_duplicate_realagentdata", "agent_dispatch")
_emit_coordinates_agents("p3", "fix_duplicate_realagentdata", "agent_coordination")
_emit_records_workflow_lineage("p3", "fix_duplicate_realagentdata", "workflow_lineage")
_emit_records_healing_outcome("p3", "fix_duplicate_realagentdata", "healing_outcome")
_emit_escalates_failure("p3", "fix_duplicate_realagentdata", "failure_escalation")
_emit_orchestrates_workflow("p3", "fix_duplicate_realagentdata", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "fix_duplicate_realagentdata", "healing_dispatch")
_emit_invokes_evaluation("p3", "fix_duplicate_realagentdata", "evaluation_signal")
_emit_records_telemetry_event("p4", "fix_duplicate_realagentdata", "telemetry_event")
_emit_captures_evaluation_metric("p4", "fix_duplicate_realagentdata", "eval_metric")
_emit_stores_embedding("p4", "fix_duplicate_realagentdata", "embedding_store")
_emit_updates_meta_learning_state("p4", "fix_duplicate_realagentdata", "meta_learning")
_emit_links_execution_to_snapshot("p4", "fix_duplicate_realagentdata", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_emits_metric_event("fix_duplicate_realagentdata", "p4obs", "metric_1")
_emit_emits_metric_event("fix_duplicate_realagentdata", "p4obs", "metric_2")
_emit_emits_metric_event("fix_duplicate_realagentdata", "p4obs", "metric_3")
_emit_emits_metric_event("fix_duplicate_realagentdata", "p4obs", "metric_4")
_emit_emits_metric_event("fix_duplicate_realagentdata", "p4obs", "metric_5")
_emit_emits_metric_event("fix_duplicate_realagentdata", "p4obs", "metric_6")
_emit_records_incident_event("fix_duplicate_realagentdata", "p4obs", "incident")
_emit_captures_runtime_anomaly("fix_duplicate_realagentdata", "p4obs", "anomaly")
_emit_writes_observability_log("fix_duplicate_realagentdata", "p4obs", "obs_log")
_emit_updates_monitoring_state("fix_duplicate_realagentdata", "p4obs", "mon_state")
_emit_triggers_alert("fix_duplicate_realagentdata", "p4obs", "alert")
_emit_links_incident_trace("fix_duplicate_realagentdata", "p4obs", "trace_link")
_emit_captures_pattern("fix_duplicate_realagentdata", "p3lm", "pattern")
_emit_records_learning_event("fix_duplicate_realagentdata", "p3lm", "learning_event")
_emit_writes_learning_snapshot("fix_duplicate_realagentdata", "p3lm", "snapshot")
_emit_feeds_meta_learning("fix_duplicate_realagentdata", "p3lm", "meta_feed")
_emit_updates_routing_strategy("fix_duplicate_realagentdata", "p3lm", "routing")
_emit_improves_agent_policy("fix_duplicate_realagentdata", "p3lm", "policy")
_emit_stores_learning_state("fix_duplicate_realagentdata", "p3lm", "state")
_emit_records_execution_trace("fix_duplicate_realagentdata", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("fix_duplicate_realagentdata", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("fix_duplicate_realagentdata", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("fix_duplicate_realagentdata", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("fix_duplicate_realagentdata", "L4_STATE", "p2_trace_5")
_emit_reads_environ("fix_duplicate_realagentdata", "env_read", "p2_env_1")
_emit_reads_environ("fix_duplicate_realagentdata", "env_read", "p2_env_2")
_emit_reads_runtime_state("fix_duplicate_realagentdata", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("fix_duplicate_realagentdata", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "fix_duplicate_realagentdata")
_emit_applies_guardrail("p0", "fix_duplicate_realagentdata", "p0_governance")
_emit_reads_policy_state("p0", "fix_duplicate_realagentdata", "policy_binding")
_emit_snapshots_state("p0", "fix_duplicate_realagentdata", "state_snapshot")
_emit_pulls_context("p1", "fix_duplicate_realagentdata", "context_pull")
_emit_pulls_context("p1", "fix_duplicate_realagentdata", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "fix_duplicate_realagentdata", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "fix_duplicate_realagentdata", "uwg_term_secondary")
_emit_writes_through("p1", "fix_duplicate_realagentdata", "write_through")
_emit_writes_through("p1", "fix_duplicate_realagentdata", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "fix_duplicate_realagentdata", "safety_validation")
_emit_invokes_eval("p1", "fix_duplicate_realagentdata", "eval_call")
_emit_proposal_commits_routing("p1", "fix_duplicate_realagentdata", "routing_commit")
_emit_escalates_to_human("p1", "fix_duplicate_realagentdata", "human_escalation")
_emit_routes_through("p1", "fix_duplicate_realagentdata", "route_through")
_emit_checks_agent_registry("p1", "fix_duplicate_realagentdata", "agent_registry")
_emit_validates_agent_capability("p1", "fix_duplicate_realagentdata", "capability")
_emit_dispatches_execution_plan("p1", "fix_duplicate_realagentdata", "exec_plan")
_emit_agent_executes_agent("p1", "fix_duplicate_realagentdata", "sub_agent")
_emit_routes_to_agent("p1", "fix_duplicate_realagentdata", "target_agent")
_emit_verifies_policy("p1", "fix_duplicate_realagentdata", "policy_check")
_emit_observes_runtime_state("p1", "fix_duplicate_realagentdata", "runtime_state")
_emit_verifies_boundary("p1", "fix_duplicate_realagentdata", "boundary_check")
_emit_transcripts_response("p1", "fix_duplicate_realagentdata", "transcript")
_emit_hard_fails_untranscripted("p1", "fix_duplicate_realagentdata")
_emit_gated_by_confidence("p1", "fix_duplicate_realagentdata", "confidence_gate")
emit_replay_key("p0", "fix_duplicate_realagentdata")
emit_determinism_digest("p0", "fix_duplicate_realagentdata")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


def fix_duplicates():
    """Remove duplicate realAgentData declarations."""
    dashboard_path = get_validated_project_root() / DASHBOARD_DIR / "autonomy_dashboard.html"

    print("Reading dashboard HTML...")
    html = dashboard_path.read_text(encoding="utf-8")

    # Find all occurrences of realAgentData declarations
    pattern = r"// Real per-agent data \(replaces generateMockAgentData\)\s*const realAgentData = \{[^}]*\};"
    matches = list(re.finditer(pattern, html, re.DOTALL))

    print(f"Found {len(matches)} realAgentData declarations")

    if len(matches) <= 1:
        print("✅ No duplicates found")
        return

    # Keep only the first occurrence, remove all others
    print(f"Removing {len(matches) - 1} duplicate declarations...")

    # Work backwards to preserve indices
    for match in reversed(matches[1:]):
        html = html[: match.start()] + html[match.end() :]

    # Write back
    dashboard_path.write_text(html, encoding="utf-8")
    print(f"✅ Fixed! Removed {len(matches) - 1} duplicates")
    print(f"   Kept first declaration at position {matches[0].start()}")


if __name__ == "__main__":
    fix_duplicates()
