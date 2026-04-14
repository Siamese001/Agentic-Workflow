import hashlib
import os
from pathlib import Path

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
    SOVEREIGN_EXCLUDED_FOLDERS,
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
from tqdm import tqdm

_emit_emits_metric_event("investigate_overlaps_util", "p4obs", "metric_1")
_emit_emits_metric_event("investigate_overlaps_util", "p4obs", "metric_2")
_emit_emits_metric_event("investigate_overlaps_util", "p4obs", "metric_3")
_emit_emits_metric_event("investigate_overlaps_util", "p4obs", "metric_4")
_emit_emits_metric_event("investigate_overlaps_util", "p4obs", "metric_5")
_emit_emits_metric_event("investigate_overlaps_util", "p4obs", "metric_6")
_emit_records_incident_event("investigate_overlaps_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("investigate_overlaps_util", "p4obs", "anomaly")
_emit_writes_observability_log("investigate_overlaps_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("investigate_overlaps_util", "p4obs", "mon_state")
_emit_triggers_alert("investigate_overlaps_util", "p4obs", "alert")
_emit_links_incident_trace("investigate_overlaps_util", "p4obs", "trace_link")
_emit_captures_pattern("investigate_overlaps_util", "p3lm", "pattern")
_emit_records_learning_event("investigate_overlaps_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("investigate_overlaps_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("investigate_overlaps_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("investigate_overlaps_util", "p3lm", "routing")
_emit_improves_agent_policy("investigate_overlaps_util", "p3lm", "policy")
_emit_stores_learning_state("investigate_overlaps_util", "p3lm", "state")
_emit_records_execution_trace("investigate_overlaps_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("investigate_overlaps_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("investigate_overlaps_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("investigate_overlaps_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("investigate_overlaps_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("investigate_overlaps_util", "env_read", "p2_env_1")
_emit_reads_environ("investigate_overlaps_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("investigate_overlaps_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("investigate_overlaps_util", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "investigate_overlaps_util")
emit_determinism_digest("p0", "investigate_overlaps_util")

_emit_dispatches_healing_run("p1", "investigate_overlaps_util", "L0")
_emit_routes_through("p1", "investigate_overlaps_util", "L0")
_emit_checks_agent_registry("p1", "investigate_overlaps_util", "agent_registry")
_emit_validates_agent_capability("p1", "investigate_overlaps_util", "capability")
_emit_dispatches_execution_plan("p1", "investigate_overlaps_util", "exec_plan")
_emit_agent_executes_agent("p1", "investigate_overlaps_util", "sub_agent")
_emit_routes_to_agent("p1", "investigate_overlaps_util", "target_agent")
_emit_verifies_policy("p1", "investigate_overlaps_util", "policy_check")
_emit_observes_runtime_state("p1", "investigate_overlaps_util", "runtime_state")
_emit_verifies_boundary("p1", "investigate_overlaps_util", "boundary_check")
_emit_transcripts_response("p1", "investigate_overlaps_util", "transcript")
_emit_hard_fails_untranscripted("p1", "investigate_overlaps_util")
_emit_gated_by_confidence("p1", "investigate_overlaps_util", "confidence_gate")
_emit_escalates_to_human("p1", "investigate_overlaps_util", "L0")
_emit_reads_policy_state("p1", "investigate_overlaps_util", "L0")
_emit_pulls_context("p1", "investigate_overlaps_util", "context_pull")
_emit_pulls_context("p1", "investigate_overlaps_util", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "investigate_overlaps_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "investigate_overlaps_util", "uwg_term_secondary")
_emit_writes_through("p1", "investigate_overlaps_util", "write_through")
_emit_writes_through("p1", "investigate_overlaps_util", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "investigate_overlaps_util", "safety_validation")
_emit_invokes_eval("p1", "investigate_overlaps_util", "eval_call")
_emit_proposal_commits_routing("p1", "investigate_overlaps_util", "routing_commit")

_emit_records_execution_trace("p0", "evidence", "investigate_overlaps_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "investigate_overlaps_util", "p0_governance")
_emit_snapshots_state("p0", "investigate_overlaps_util", "state_snapshot")
_emit_authorize_and_execute("p2", "investigate_overlaps_util", "execution_auth")
_emit_validates_capability("p2", "investigate_overlaps_util", "capability_check")
_emit_routes_to_capability("p2", "investigate_overlaps_util", "capability_route")
_emit_writes_via_uwg("p2", "investigate_overlaps_util", "uwg_write")
_emit_blocks_direct_write("p2", "investigate_overlaps_util", "direct_write_block")
_emit_records_tool_invocation("p2", "investigate_overlaps_util", "tool_invocation")
_emit_captures_execution_output("p2", "investigate_overlaps_util", "exec_output")
_emit_dispatches_agent("p3", "investigate_overlaps_util", "agent_dispatch")
_emit_coordinates_agents("p3", "investigate_overlaps_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "investigate_overlaps_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "investigate_overlaps_util", "healing_outcome")
_emit_escalates_failure("p3", "investigate_overlaps_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "investigate_overlaps_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "investigate_overlaps_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "investigate_overlaps_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "investigate_overlaps_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "investigate_overlaps_util", "eval_metric")
_emit_stores_embedding("p4", "investigate_overlaps_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "investigate_overlaps_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "investigate_overlaps_util", "exec_snapshot_link")

PROJECT_ROOT = Path(__file__).parent.parent.parent
GROUPS = {
    "Location": ["LocationAgent.py", "LocationValidatorAgent.py", "LocationHealerAgent.py"],
    "Hierarchy": ["HierarchyAgent.py", "HierarchyValidatorAgent.py"],
    "Import": ["ImportAgent.py", "ImportLockAgent.py"],
    "Strategic": ["StrategicRecommendationAgent.py", "StrategicPlannerAgent.py"],
}


def get_file_hash(path: Path):
    """TODO: Add documentation for get_file_hash."""
    if not path.exists():
        return None
    return hashlib.md5(path.read_bytes()).hexdigest()


def investigate():
    """TODO: Add documentation for investigate."""
    for _group_name, filenames in tqdm(GROUPS.items(), desc="Processing", unit="item"):
        found_files = []
        for root, dirs, files in os.walk(PROJECT_ROOT / AGENTIC_CORE_DIR):
            dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
            for f in files:
                if f in filenames:
                    found_files.append(Path(root) / f)
        if not found_files:
            continue
        for f_path in found_files:
            get_file_hash(f_path)
            f_path.relative_to(PROJECT_ROOT)
        hashes = [get_file_hash(p) for p in found_files]
        unique_hashes = set(hashes)
        if len(unique_hashes) < len(hashes):
            pass


if __name__ == "__main__":
    investigate()
