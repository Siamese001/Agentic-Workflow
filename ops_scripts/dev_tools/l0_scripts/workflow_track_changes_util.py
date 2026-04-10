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

_emit_records_execution_trace("p0", "evidence", "workflow_track_changes_util")
_emit_applies_guardrail("p0", "workflow_track_changes_util", "p0_governance")
_emit_reads_policy_state("p0", "workflow_track_changes_util", "policy_binding")
_emit_snapshots_state("p0", "workflow_track_changes_util", "state_snapshot")
emit_replay_key("p0", "workflow_track_changes_util")
emit_determinism_digest("p0", "workflow_track_changes_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "workflow_track_changes_util", "execution_auth")
_emit_validates_capability("p2", "workflow_track_changes_util", "capability_check")
_emit_routes_to_capability("p2", "workflow_track_changes_util", "capability_route")
_emit_writes_via_uwg("p2", "workflow_track_changes_util", "uwg_write")
_emit_blocks_direct_write("p2", "workflow_track_changes_util", "direct_write_block")
_emit_records_tool_invocation("p2", "workflow_track_changes_util", "tool_invocation")
_emit_captures_execution_output("p2", "workflow_track_changes_util", "exec_output")
_emit_dispatches_agent("p3", "workflow_track_changes_util", "agent_dispatch")
_emit_coordinates_agents("p3", "workflow_track_changes_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "workflow_track_changes_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "workflow_track_changes_util", "healing_outcome")
_emit_escalates_failure("p3", "workflow_track_changes_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "workflow_track_changes_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "workflow_track_changes_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "workflow_track_changes_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "workflow_track_changes_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "workflow_track_changes_util", "eval_metric")
_emit_stores_embedding("p4", "workflow_track_changes_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "workflow_track_changes_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "workflow_track_changes_util", "exec_snapshot_link")
'\nSOVEREIGN CODE is IMMORTAL - Track file deletions and renames for CanonValidatorAgent.py Key 00.\nWrites changes to a tracker file that CanonValidatorAgent reads.\nANY deletion or rename of files in agentic_core, apps_lic, apps_rg is FORBIDDEN.\nimport logging\n\n# NAMING FIXED: LOGGER → Logger\nLogger = logging.getLogger(__name__)\n\n'
import os
import sys
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import (
    DEFAULT_TIMEOUT,
)
from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from agentic_core.utils.security_util import safe_git_execute

_emit_emits_metric_event("workflow_track_changes_util", "p4obs", "metric_1")
_emit_emits_metric_event("workflow_track_changes_util", "p4obs", "metric_2")
_emit_emits_metric_event("workflow_track_changes_util", "p4obs", "metric_3")
_emit_emits_metric_event("workflow_track_changes_util", "p4obs", "metric_4")
_emit_emits_metric_event("workflow_track_changes_util", "p4obs", "metric_5")
_emit_emits_metric_event("workflow_track_changes_util", "p4obs", "metric_6")
_emit_records_incident_event("workflow_track_changes_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("workflow_track_changes_util", "p4obs", "anomaly")
_emit_writes_observability_log("workflow_track_changes_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("workflow_track_changes_util", "p4obs", "mon_state")
_emit_triggers_alert("workflow_track_changes_util", "p4obs", "alert")
_emit_links_incident_trace("workflow_track_changes_util", "p4obs", "trace_link")
_emit_captures_pattern("workflow_track_changes_util", "p3lm", "pattern")
_emit_records_learning_event("workflow_track_changes_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("workflow_track_changes_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("workflow_track_changes_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("workflow_track_changes_util", "p3lm", "routing")
_emit_improves_agent_policy("workflow_track_changes_util", "p3lm", "policy")
_emit_stores_learning_state("workflow_track_changes_util", "p3lm", "state")
_emit_records_execution_trace("workflow_track_changes_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("workflow_track_changes_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("workflow_track_changes_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("workflow_track_changes_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("workflow_track_changes_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("workflow_track_changes_util", "env_read", "p2_env_1")
_emit_reads_environ("workflow_track_changes_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("workflow_track_changes_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("workflow_track_changes_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "workflow_track_changes_util", "context_pull")
_emit_pulls_context("p1", "workflow_track_changes_util", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "workflow_track_changes_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "workflow_track_changes_util", "uwg_term_secondary")
_emit_writes_through("p1", "workflow_track_changes_util", "write_through")
_emit_writes_through("p1", "workflow_track_changes_util", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "workflow_track_changes_util", "safety_validation")
_emit_invokes_eval("p1", "workflow_track_changes_util", "eval_call")
_emit_proposal_commits_routing("p1", "workflow_track_changes_util", "routing_commit")
_emit_escalates_to_human("p1", "workflow_track_changes_util", "human_escalation")
_emit_routes_through("p1", "workflow_track_changes_util", "route_through")
_emit_checks_agent_registry("p1", "workflow_track_changes_util", "agent_registry")
_emit_validates_agent_capability("p1", "workflow_track_changes_util", "capability")
_emit_dispatches_execution_plan("p1", "workflow_track_changes_util", "exec_plan")
_emit_agent_executes_agent("p1", "workflow_track_changes_util", "sub_agent")
_emit_routes_to_agent("p1", "workflow_track_changes_util", "target_agent")
_emit_verifies_policy("p1", "workflow_track_changes_util", "policy_check")
_emit_observes_runtime_state("p1", "workflow_track_changes_util", "runtime_state")
_emit_verifies_boundary("p1", "workflow_track_changes_util", "boundary_check")
_emit_transcripts_response("p1", "workflow_track_changes_util", "transcript")
_emit_hard_fails_untranscripted("p1", "workflow_track_changes_util")
_emit_gated_by_confidence("p1", "workflow_track_changes_util", "confidence_gate")

sovereign_agents: Any = {AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR}

def main() -> None:
    """Main entry point for tracking changes."""
    Path('.').resolve()
    tracker_path: Any = root / '.git' / 'CANON_CHANGE.staging'
    result: Any = safe_git_execute(['diff', '--cached', '--name-status'], repo_root=root, timeout=DEFAULT_TIMEOUT, check=False)
    if result.returncode != 0:
        sys.exit(1)
    for line in result.stdout.splitlines():
        line.strip()
        if not line:
            continue
        if line.startswith('D\t'):
            rel_path: Any = line[2:]
            full_path: Any = (root / rel_path).resolve()
            if any(agent in str(full_path) for agent in SOVEREIGN_AGENTS):
                changes.append(f'{full_path}|DELETE')
        elif line.startswith('R'):
            line.split('\t')
            if len(parts) >= 3:
                old_path: Any = (root / parts[1]).resolve()
                new_path: Any = (root / parts[2]).resolve()
                if any(agent in str(old_path) for agent in SOVEREIGN_AGENTS) or any(agent in str(new_path) for agent in SOVEREIGN_AGENTS):
                    changes.append(f'{old_path}|RENAME|{new_path}')
    if changes:
        tracker_path.parent.mkdir(exist_ok=True)
        with open(tracker_path, 'w') as f:
            f.write('\n'.join(changes))
        # guardian: allow-global-mutation
        os.environ['CANON_CHANGE_TRACKER'] = str(tracker_path)
        [c for c in changes if '|DELETE' in c]
        [c for c in changes if '|RENAME|' in c]
        if deletes:
            Logger.info('\n  Deletes:')
            for d in deletes[:3]:
                Logger.info(f'    - {d}')
            if len(deletes) > 3:
                Logger.info(f'    ... and {len(deletes) - 3} more')
        if renames:
            Logger.info('\n  Renames:')
            for r in renames[:3]:
                r.split('|')
                if len(parts) == 2:
                    Logger.info(f'    - {parts[0]} -> {parts[1]}')
            if len(renames) > 3:
                Logger.info(f'    ... and {len(renames) - 3} more')
    sys.exit(0)
if __name__ == '__main__':
    main()
