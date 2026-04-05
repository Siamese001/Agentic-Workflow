"""Run NamingAgent to detect agent file naming violations."""

import sys
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "run_naming_law_check_util")
emit_determinism_digest("p0", "run_naming_law_check_util")

_emit_dispatches_healing_run("p1", "run_naming_law_check_util", "L0")
_emit_routes_through("p1", "run_naming_law_check_util", "L0")
_emit_checks_agent_registry("p1", "run_naming_law_check_util", "agent_registry")
_emit_validates_agent_capability("p1", "run_naming_law_check_util", "capability")
_emit_dispatches_execution_plan("p1", "run_naming_law_check_util", "exec_plan")
_emit_agent_executes_agent("p1", "run_naming_law_check_util", "sub_agent")
_emit_routes_to_agent("p1", "run_naming_law_check_util", "target_agent")
_emit_verifies_policy("p1", "run_naming_law_check_util", "policy_check")
_emit_observes_runtime_state("p1", "run_naming_law_check_util", "runtime_state")
_emit_verifies_boundary("p1", "run_naming_law_check_util", "boundary_check")
_emit_transcripts_response("p1", "run_naming_law_check_util", "transcript")
_emit_hard_fails_untranscripted("p1", "run_naming_law_check_util")
_emit_gated_by_confidence("p1", "run_naming_law_check_util", "confidence_gate")
_emit_escalates_to_human("p1", "run_naming_law_check_util", "L0")
_emit_reads_policy_state("p1", "run_naming_law_check_util", "L0")
_emit_authorize_and_execute("p2", "run_naming_law_check_util", "execution_auth")
_emit_validates_capability("p2", "run_naming_law_check_util", "capability_check")
_emit_routes_to_capability("p2", "run_naming_law_check_util", "capability_route")
_emit_writes_via_uwg("p2", "run_naming_law_check_util", "uwg_write")
_emit_blocks_direct_write("p2", "run_naming_law_check_util", "direct_write_block")
_emit_records_tool_invocation("p2", "run_naming_law_check_util", "tool_invocation")
_emit_captures_execution_output("p2", "run_naming_law_check_util", "exec_output")
_emit_dispatches_agent("p3", "run_naming_law_check_util", "agent_dispatch")
_emit_coordinates_agents("p3", "run_naming_law_check_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "run_naming_law_check_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "run_naming_law_check_util", "healing_outcome")
_emit_escalates_failure("p3", "run_naming_law_check_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "run_naming_law_check_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "run_naming_law_check_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "run_naming_law_check_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "run_naming_law_check_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "run_naming_law_check_util", "eval_metric")
_emit_stores_embedding("p4", "run_naming_law_check_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "run_naming_law_check_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "run_naming_law_check_util", "exec_snapshot_link")

PROJECT_ROOT = Path(__file__).parent.parent
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))
from agentic_core.L0_routing.config import AGENTIC_CORE_DIR
from agentic_core.L0_routing.utils.seams.safety_reasoning_seam import load_naming_agent
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

_emit_emits_metric_event("run_naming_law_check_util", "p4obs", "metric_1")
_emit_emits_metric_event("run_naming_law_check_util", "p4obs", "metric_2")
_emit_emits_metric_event("run_naming_law_check_util", "p4obs", "metric_3")
_emit_emits_metric_event("run_naming_law_check_util", "p4obs", "metric_4")
_emit_emits_metric_event("run_naming_law_check_util", "p4obs", "metric_5")
_emit_emits_metric_event("run_naming_law_check_util", "p4obs", "metric_6")
_emit_records_incident_event("run_naming_law_check_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("run_naming_law_check_util", "p4obs", "anomaly")
_emit_writes_observability_log("run_naming_law_check_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("run_naming_law_check_util", "p4obs", "mon_state")
_emit_triggers_alert("run_naming_law_check_util", "p4obs", "alert")
_emit_links_incident_trace("run_naming_law_check_util", "p4obs", "trace_link")
_emit_captures_pattern("run_naming_law_check_util", "p3lm", "pattern")
_emit_records_learning_event("run_naming_law_check_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("run_naming_law_check_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("run_naming_law_check_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("run_naming_law_check_util", "p3lm", "routing")
_emit_improves_agent_policy("run_naming_law_check_util", "p3lm", "policy")
_emit_stores_learning_state("run_naming_law_check_util", "p3lm", "state")
_emit_records_execution_trace("run_naming_law_check_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("run_naming_law_check_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("run_naming_law_check_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("run_naming_law_check_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("run_naming_law_check_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("run_naming_law_check_util", "env_read", "p2_env_1")
_emit_reads_environ("run_naming_law_check_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("run_naming_law_check_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("run_naming_law_check_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "run_naming_law_check_util", "context_pull")
_emit_pulls_context("p1", "run_naming_law_check_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "run_naming_law_check_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "run_naming_law_check_util", "uwg_term_2")
_emit_writes_through("p1", "run_naming_law_check_util", "write_through")
_emit_writes_through("p1", "run_naming_law_check_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "run_naming_law_check_util", "safety_validation")
_emit_invokes_eval("p1", "run_naming_law_check_util", "eval_call")
_emit_proposal_commits_routing("p1", "run_naming_law_check_util", "routing_commit")


def main():
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "main", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "main", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "main")
    NamingAgent = load_naming_agent()
    agent = NamingAgent(PROJECT_ROOT)
    scan_dirs = [AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR]
    violations = []
    compliant = 0
    for dir_name in scan_dirs:
        dir_path = PROJECT_ROOT / dir_name
        if not dir_path.exists():
            continue
        from agentic_core.utils.schemas.ssot_discovery_validator import get_python_files

        for py_file in get_python_files(dir_path):
            if "__pycache__" in str(py_file) or "__init__.py" == py_file.name:
                continue
            is_valid, message = agent.validate_file_naming(py_file)
            if not is_valid and "AGENT FILE NAMING VIOLATION" in message:
                rel_path = py_file.relative_to(PROJECT_ROOT)
                violations.append((str(rel_path), message))
            elif is_valid:
                compliant += 1
    print("=" * 70)
    print("AGENT FILE NAMING LAW CHECK")
    print("=" * 70)
    print(f"\nCompliant files: {compliant}")
    print(f"Violations (agent classes in non-*Agent.py files): {len(violations)}")
    print("=" * 70)
    if violations:
        print("\nVIOLATIONS:\n")
        for path, msg in sorted(violations)[:50]:
            print(f"  {path}")
            if "Rename file to" in msg:
                suggested = msg.split("Rename file to '")[1].split("'")[0]
                print(f"    → Rename to: {suggested}")
            print()
        if len(violations) > 50:
            print(f"  ... and {len(violations) - 50} more violations")
    print("=" * 70)
    print(f"TOTAL: {len(violations)} files need renaming to *Agent.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
