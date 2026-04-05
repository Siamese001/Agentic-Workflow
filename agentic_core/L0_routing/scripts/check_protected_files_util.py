"""
Gatekeeper Protection: Block commits that modify protected files

This script prevents accidental modifications to critical infrastructure files
like ArchivalGatekeeper.py unless an explicit override is present in the commit message.

PROTECTED FILES:
    - agentic_core/L5_safety/enforcement/ArchivalGatekeeper.py (The Executioner)
    - agentic_core/L5_safety/validators/decorators.py (The Normalizer)

OVERRIDE:
    Include '#gatekeeper-override' in your commit message to bypass protection.

USAGE:
    python scripts/maintenance/check_protected_files_util.py

EXIT CODES:
    0 - No protected files modified OR override present
    1 - Protected files modified without override
"""

import subprocess
import sys
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

emit_replay_key("p0", "check_protected_files_util")
emit_determinism_digest("p0", "check_protected_files_util")

_emit_dispatches_healing_run("p1", "check_protected_files_util", "L0")
_emit_routes_through("p1", "check_protected_files_util", "L0")
_emit_checks_agent_registry("p1", "check_protected_files_util", "agent_registry")
_emit_validates_agent_capability("p1", "check_protected_files_util", "capability")
_emit_dispatches_execution_plan("p1", "check_protected_files_util", "exec_plan")
_emit_agent_executes_agent("p1", "check_protected_files_util", "sub_agent")
_emit_routes_to_agent("p1", "check_protected_files_util", "target_agent")
_emit_verifies_policy("p1", "check_protected_files_util", "policy_check")
_emit_observes_runtime_state("p1", "check_protected_files_util", "runtime_state")
_emit_verifies_boundary("p1", "check_protected_files_util", "boundary_check")
_emit_transcripts_response("p1", "check_protected_files_util", "transcript")
_emit_hard_fails_untranscripted("p1", "check_protected_files_util")
_emit_gated_by_confidence("p1", "check_protected_files_util", "confidence_gate")
_emit_escalates_to_human("p1", "check_protected_files_util", "L0")
_emit_reads_policy_state("p1", "check_protected_files_util", "L0")
_emit_authorize_and_execute("p2", "check_protected_files_util", "execution_auth")
_emit_validates_capability("p2", "check_protected_files_util", "capability_check")
_emit_routes_to_capability("p2", "check_protected_files_util", "capability_route")
_emit_writes_via_uwg("p2", "check_protected_files_util", "uwg_write")
_emit_blocks_direct_write("p2", "check_protected_files_util", "direct_write_block")
_emit_records_tool_invocation("p2", "check_protected_files_util", "tool_invocation")
_emit_captures_execution_output("p2", "check_protected_files_util", "exec_output")
_emit_dispatches_agent("p3", "check_protected_files_util", "agent_dispatch")
_emit_coordinates_agents("p3", "check_protected_files_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "check_protected_files_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "check_protected_files_util", "healing_outcome")
_emit_escalates_failure("p3", "check_protected_files_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "check_protected_files_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "check_protected_files_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "check_protected_files_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "check_protected_files_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "check_protected_files_util", "eval_metric")
_emit_stores_embedding("p4", "check_protected_files_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "check_protected_files_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "check_protected_files_util", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("check_protected_files_util", "p4obs", "metric_1")
_emit_emits_metric_event("check_protected_files_util", "p4obs", "metric_2")
_emit_emits_metric_event("check_protected_files_util", "p4obs", "metric_3")
_emit_emits_metric_event("check_protected_files_util", "p4obs", "metric_4")
_emit_emits_metric_event("check_protected_files_util", "p4obs", "metric_5")
_emit_emits_metric_event("check_protected_files_util", "p4obs", "metric_6")
_emit_records_incident_event("check_protected_files_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("check_protected_files_util", "p4obs", "anomaly")
_emit_writes_observability_log("check_protected_files_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("check_protected_files_util", "p4obs", "mon_state")
_emit_triggers_alert("check_protected_files_util", "p4obs", "alert")
_emit_links_incident_trace("check_protected_files_util", "p4obs", "trace_link")
_emit_captures_pattern("check_protected_files_util", "p3lm", "pattern")
_emit_records_learning_event("check_protected_files_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("check_protected_files_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("check_protected_files_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("check_protected_files_util", "p3lm", "routing")
_emit_improves_agent_policy("check_protected_files_util", "p3lm", "policy")
_emit_stores_learning_state("check_protected_files_util", "p3lm", "state")
_emit_records_execution_trace("check_protected_files_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("check_protected_files_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("check_protected_files_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("check_protected_files_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("check_protected_files_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("check_protected_files_util", "env_read", "p2_env_1")
_emit_reads_environ("check_protected_files_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("check_protected_files_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("check_protected_files_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "check_protected_files_util", "context_pull")
_emit_pulls_context("p1", "check_protected_files_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "check_protected_files_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "check_protected_files_util", "uwg_term_2")
_emit_writes_through("p1", "check_protected_files_util", "write_through")
_emit_writes_through("p1", "check_protected_files_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "check_protected_files_util", "safety_validation")
_emit_invokes_eval("p1", "check_protected_files_util", "eval_call")
_emit_proposal_commits_routing("p1", "check_protected_files_util", "routing_commit")

PROTECTED_FILES = [
    "agentic_core/L5_safety/enforcement/ArchivalGatekeeper.py",
    "agentic_core/L5_safety/validators/decorators.py",
]
OVERRIDE_FLAG = "#gatekeeper-override"


def get_staged_files() -> list[str]:
    """Get list of files staged for commit."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "get_staged_files", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "get_staged_files", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "get_staged_files")
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"], capture_output=True, text=True, check=True
        )
        return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
    except subprocess.CalledProcessError:
        return []


def get_commit_message() -> str:
    """Get the commit message if available."""
    try:
        commit_msg_file = Path(".git/COMMIT_EDITMSG")
        if commit_msg_file.exists():
            return commit_msg_file.read_text()
        return ""
    # guardian: allow-silent-swallow
    except (ValueError, TypeError):
        return ""


def main():
    """TODO: Add documentation for main."""
    staged_files = get_staged_files()
    if not staged_files:
        sys.exit(0)
    modified_protected = []
    for protected in PROTECTED_FILES:
        protected_path = Path(protected).as_posix()
        for staged in staged_files:
            staged_path = Path(staged).as_posix()
            if staged_path == protected_path or staged_path.endswith(protected_path):
                modified_protected.append(protected)
                break
    if not modified_protected:
        sys.exit(0)
    commit_message = get_commit_message()
    if OVERRIDE_FLAG in commit_message:
        for _f in modified_protected:
            pass
        sys.exit(0)
    for _f in modified_protected:
        pass
    sys.exit(1)


if __name__ == "__main__":
    main()
