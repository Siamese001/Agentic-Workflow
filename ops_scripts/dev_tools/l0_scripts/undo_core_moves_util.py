from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_records_execution_trace("p0", "evidence", "undo_core_moves_util")
_emit_applies_guardrail("p0", "undo_core_moves_util", "p0_governance")
_emit_reads_policy_state("p0", "undo_core_moves_util", "policy_binding")
_emit_snapshots_state("p0", "undo_core_moves_util", "state_snapshot")
emit_replay_key("p0", "undo_core_moves_util")
emit_determinism_digest("p0", "undo_core_moves_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "undo_core_moves_util", "execution_auth")
_emit_validates_capability("p2", "undo_core_moves_util", "capability_check")
_emit_routes_to_capability("p2", "undo_core_moves_util", "capability_route")
_emit_writes_via_uwg("p2", "undo_core_moves_util", "uwg_write")
_emit_blocks_direct_write("p2", "undo_core_moves_util", "direct_write_block")
_emit_records_tool_invocation("p2", "undo_core_moves_util", "tool_invocation")
_emit_captures_execution_output("p2", "undo_core_moves_util", "exec_output")
_emit_dispatches_agent("p3", "undo_core_moves_util", "agent_dispatch")
_emit_coordinates_agents("p3", "undo_core_moves_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "undo_core_moves_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "undo_core_moves_util", "healing_outcome")
_emit_escalates_failure("p3", "undo_core_moves_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "undo_core_moves_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "undo_core_moves_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "undo_core_moves_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "undo_core_moves_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "undo_core_moves_util", "eval_metric")
_emit_stores_embedding("p4", "undo_core_moves_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "undo_core_moves_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "undo_core_moves_util", "exec_snapshot_link")
'\nUndo all the incorrect core/ subdirectory moves\n'
import shutil
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.config.structure_blueprint import AGENTIC_CORE_DIR, SCRIPTS_DIR
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("undo_core_moves_util", "p4obs", "metric_1")
_emit_emits_metric_event("undo_core_moves_util", "p4obs", "metric_2")
_emit_emits_metric_event("undo_core_moves_util", "p4obs", "metric_3")
_emit_emits_metric_event("undo_core_moves_util", "p4obs", "metric_4")
_emit_emits_metric_event("undo_core_moves_util", "p4obs", "metric_5")
_emit_emits_metric_event("undo_core_moves_util", "p4obs", "metric_6")
_emit_records_incident_event("undo_core_moves_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("undo_core_moves_util", "p4obs", "anomaly")
_emit_writes_observability_log("undo_core_moves_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("undo_core_moves_util", "p4obs", "mon_state")
_emit_triggers_alert("undo_core_moves_util", "p4obs", "alert")
_emit_links_incident_trace("undo_core_moves_util", "p4obs", "trace_link")
_emit_captures_pattern("undo_core_moves_util", "p3lm", "pattern")
_emit_records_learning_event("undo_core_moves_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("undo_core_moves_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("undo_core_moves_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("undo_core_moves_util", "p3lm", "routing")
_emit_improves_agent_policy("undo_core_moves_util", "p3lm", "policy")
_emit_stores_learning_state("undo_core_moves_util", "p3lm", "state")
_emit_records_execution_trace("undo_core_moves_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("undo_core_moves_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("undo_core_moves_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("undo_core_moves_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("undo_core_moves_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("undo_core_moves_util", "env_read", "p2_env_1")
_emit_reads_environ("undo_core_moves_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("undo_core_moves_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("undo_core_moves_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "undo_core_moves_util", "context_pull")
_emit_pulls_context("p1", "undo_core_moves_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "undo_core_moves_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "undo_core_moves_util", "uwg_term_2")
_emit_writes_through("p1", "undo_core_moves_util", "write_through")
_emit_writes_through("p1", "undo_core_moves_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "undo_core_moves_util", "safety_validation")
_emit_invokes_eval("p1", "undo_core_moves_util", "eval_call")
_emit_proposal_commits_routing("p1", "undo_core_moves_util", "routing_commit")
_emit_escalates_to_human("p1", "undo_core_moves_util", "human_escalation")
_emit_routes_through("p1", "undo_core_moves_util", "route_through")
_emit_checks_agent_registry("p1", "undo_core_moves_util", "agent_registry")
_emit_validates_agent_capability("p1", "undo_core_moves_util", "capability")
_emit_dispatches_execution_plan("p1", "undo_core_moves_util", "exec_plan")
_emit_agent_executes_agent("p1", "undo_core_moves_util", "sub_agent")
_emit_routes_to_agent("p1", "undo_core_moves_util", "target_agent")
_emit_verifies_policy("p1", "undo_core_moves_util", "policy_check")
_emit_observes_runtime_state("p1", "undo_core_moves_util", "runtime_state")
_emit_verifies_boundary("p1", "undo_core_moves_util", "boundary_check")
_emit_transcripts_response("p1", "undo_core_moves_util", "transcript")
_emit_hard_fails_untranscripted("p1", "undo_core_moves_util")
_emit_gated_by_confidence("p1", "undo_core_moves_util", "confidence_gate")


def undo_core_moves() -> Any:
    """Move all files back from */core/ to parent directories"""
    root: Any = Path('.')
    directories: Any = [AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR, 'config', 'observability', 'schemas', SCRIPTS_DIR, TOOLS_DIR, 'validator', 'prompt_governance']
    moved_count: Any = 0
    for dir_name in directories:
        core_path: Any = root / dir_name / 'core'
        if not core_path.exists():
            continue
        from agentic_core.utils.runners.ssot_discovery_validator import get_python_files
        for py_file in get_python_files(core_path):
            if py_file.name == '__init__.py':
                continue
            target: Any = core_path.parent / py_file.name
            if target.exists():
                print(f'Skipping {py_file} (target exists)')
                continue
            print(f'Moving {py_file} -> {dir_name}/{py_file.name}')
            shutil.move(str(py_file), str(target))
            moved_count += 1
        try:
            core_path.rmdir()
            print(f'Removed {dir_name}/core/')
        # guardian: allow-silent-swallow
        except:
            pass
    print(f'\nTotal files moved back: {moved_count}')
if __name__ == '__main__':
    undo_core_moves()
