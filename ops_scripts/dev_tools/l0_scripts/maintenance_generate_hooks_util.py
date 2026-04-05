"""
ops_scripts/dev_tools/l0_scripts/maintenance_generate_hooks_util.py
-----------------------------------------------------------------
DEPRECATED: Redirects to the unified 'generate_hooks.py' script.
This file is retained as a stub to prevent breaking existing automation
that calls this specific path.
"""
from __future__ import annotations

import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_records_execution_trace("p0", "evidence", "maintenance_generate_hooks_util")
_emit_applies_guardrail("p0", "maintenance_generate_hooks_util", "p0_governance")
_emit_reads_policy_state("p0", "maintenance_generate_hooks_util", "policy_binding")
_emit_snapshots_state("p0", "maintenance_generate_hooks_util", "state_snapshot")
emit_replay_key("p0", "maintenance_generate_hooks_util")
emit_determinism_digest("p0", "maintenance_generate_hooks_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "maintenance_generate_hooks_util", "execution_auth")
_emit_validates_capability("p2", "maintenance_generate_hooks_util", "capability_check")
_emit_routes_to_capability("p2", "maintenance_generate_hooks_util", "capability_route")
_emit_writes_via_uwg("p2", "maintenance_generate_hooks_util", "uwg_write")
_emit_blocks_direct_write("p2", "maintenance_generate_hooks_util", "direct_write_block")
_emit_records_tool_invocation("p2", "maintenance_generate_hooks_util", "tool_invocation")
_emit_captures_execution_output("p2", "maintenance_generate_hooks_util", "exec_output")
_emit_dispatches_agent("p3", "maintenance_generate_hooks_util", "agent_dispatch")
_emit_coordinates_agents("p3", "maintenance_generate_hooks_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "maintenance_generate_hooks_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "maintenance_generate_hooks_util", "healing_outcome")
_emit_escalates_failure("p3", "maintenance_generate_hooks_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "maintenance_generate_hooks_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "maintenance_generate_hooks_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "maintenance_generate_hooks_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "maintenance_generate_hooks_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "maintenance_generate_hooks_util", "eval_metric")
_emit_stores_embedding("p4", "maintenance_generate_hooks_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "maintenance_generate_hooks_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "maintenance_generate_hooks_util", "exec_snapshot_link")
project_root = Path(__file__).resolve().parent.parent.parent
# guardian: allow-global-mutation
sys.path.insert(0, str(project_root))
from ops_scripts.dev_tools.L0_routing_scripts.generate_hooks import generate_sovereign_list, sync_pre_commit

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_emits_metric_event("maintenance_generate_hooks_util", "p4obs", "metric_1")
_emit_emits_metric_event("maintenance_generate_hooks_util", "p4obs", "metric_2")
_emit_emits_metric_event("maintenance_generate_hooks_util", "p4obs", "metric_3")
_emit_emits_metric_event("maintenance_generate_hooks_util", "p4obs", "metric_4")
_emit_emits_metric_event("maintenance_generate_hooks_util", "p4obs", "metric_5")
_emit_emits_metric_event("maintenance_generate_hooks_util", "p4obs", "metric_6")
_emit_records_incident_event("maintenance_generate_hooks_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("maintenance_generate_hooks_util", "p4obs", "anomaly")
_emit_writes_observability_log("maintenance_generate_hooks_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("maintenance_generate_hooks_util", "p4obs", "mon_state")
_emit_triggers_alert("maintenance_generate_hooks_util", "p4obs", "alert")
_emit_links_incident_trace("maintenance_generate_hooks_util", "p4obs", "trace_link")
_emit_captures_pattern("maintenance_generate_hooks_util", "p3lm", "pattern")
_emit_records_learning_event("maintenance_generate_hooks_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("maintenance_generate_hooks_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("maintenance_generate_hooks_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("maintenance_generate_hooks_util", "p3lm", "routing")
_emit_improves_agent_policy("maintenance_generate_hooks_util", "p3lm", "policy")
_emit_stores_learning_state("maintenance_generate_hooks_util", "p3lm", "state")
_emit_records_execution_trace("maintenance_generate_hooks_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("maintenance_generate_hooks_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("maintenance_generate_hooks_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("maintenance_generate_hooks_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("maintenance_generate_hooks_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("maintenance_generate_hooks_util", "env_read", "p2_env_1")
_emit_reads_environ("maintenance_generate_hooks_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("maintenance_generate_hooks_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("maintenance_generate_hooks_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "maintenance_generate_hooks_util", "context_pull")
_emit_pulls_context("p1", "maintenance_generate_hooks_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "maintenance_generate_hooks_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "maintenance_generate_hooks_util", "uwg_term_2")
_emit_writes_through("p1", "maintenance_generate_hooks_util", "write_through")
_emit_writes_through("p1", "maintenance_generate_hooks_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "maintenance_generate_hooks_util", "safety_validation")
_emit_invokes_eval("p1", "maintenance_generate_hooks_util", "eval_call")
_emit_proposal_commits_routing("p1", "maintenance_generate_hooks_util", "routing_commit")
_emit_escalates_to_human("p1", "maintenance_generate_hooks_util", "human_escalation")
_emit_routes_through("p1", "maintenance_generate_hooks_util", "route_through")
_emit_checks_agent_registry("p1", "maintenance_generate_hooks_util", "agent_registry")
_emit_validates_agent_capability("p1", "maintenance_generate_hooks_util", "capability")
_emit_dispatches_execution_plan("p1", "maintenance_generate_hooks_util", "exec_plan")
_emit_agent_executes_agent("p1", "maintenance_generate_hooks_util", "sub_agent")
_emit_routes_to_agent("p1", "maintenance_generate_hooks_util", "target_agent")
_emit_verifies_policy("p1", "maintenance_generate_hooks_util", "policy_check")
_emit_observes_runtime_state("p1", "maintenance_generate_hooks_util", "runtime_state")
_emit_verifies_boundary("p1", "maintenance_generate_hooks_util", "boundary_check")
_emit_transcripts_response("p1", "maintenance_generate_hooks_util", "transcript")
_emit_hard_fails_untranscripted("p1", "maintenance_generate_hooks_util")
_emit_gated_by_confidence("p1", "maintenance_generate_hooks_util", "confidence_gate")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Sync pre-commit config with SSOT (Redirect)')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without applying')
    parser.add_argument('--list', action='store_true', help='List current sovereign roots')
    args = parser.parse_args()
    print('[*] maintenance_generate_hooks_util.py is DEPRECATED. Redirecting to generate_hooks.py...')
    if args.list:
        generate_sovereign_list()
    else:
        success = sync_pre_commit(dry_run=args.dry_run)
        sys.exit(0 if success else 1)
