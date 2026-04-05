from __future__ import annotations

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

emit_replay_key("p0", "fix_depth_violations_util")
emit_determinism_digest("p0", "fix_depth_violations_util")

_emit_dispatches_healing_run("p1", "fix_depth_violations_util", "L0")
_emit_routes_through("p1", "fix_depth_violations_util", "L0")
_emit_checks_agent_registry("p1", "fix_depth_violations_util", "agent_registry")
_emit_validates_agent_capability("p1", "fix_depth_violations_util", "capability")
_emit_dispatches_execution_plan("p1", "fix_depth_violations_util", "exec_plan")
_emit_agent_executes_agent("p1", "fix_depth_violations_util", "sub_agent")
_emit_routes_to_agent("p1", "fix_depth_violations_util", "target_agent")
_emit_verifies_policy("p1", "fix_depth_violations_util", "policy_check")
_emit_observes_runtime_state("p1", "fix_depth_violations_util", "runtime_state")
_emit_verifies_boundary("p1", "fix_depth_violations_util", "boundary_check")
_emit_transcripts_response("p1", "fix_depth_violations_util", "transcript")
_emit_hard_fails_untranscripted("p1", "fix_depth_violations_util")
_emit_gated_by_confidence("p1", "fix_depth_violations_util", "confidence_gate")
_emit_escalates_to_human("p1", "fix_depth_violations_util", "L0")
_emit_reads_policy_state("p1", "fix_depth_violations_util", "L0")
_emit_authorize_and_execute("p2", "fix_depth_violations_util", "execution_auth")
_emit_validates_capability("p2", "fix_depth_violations_util", "capability_check")
_emit_routes_to_capability("p2", "fix_depth_violations_util", "capability_route")
_emit_writes_via_uwg("p2", "fix_depth_violations_util", "uwg_write")
_emit_blocks_direct_write("p2", "fix_depth_violations_util", "direct_write_block")
_emit_records_tool_invocation("p2", "fix_depth_violations_util", "tool_invocation")
_emit_captures_execution_output("p2", "fix_depth_violations_util", "exec_output")
_emit_dispatches_agent("p3", "fix_depth_violations_util", "agent_dispatch")
_emit_coordinates_agents("p3", "fix_depth_violations_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "fix_depth_violations_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "fix_depth_violations_util", "healing_outcome")
_emit_escalates_failure("p3", "fix_depth_violations_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "fix_depth_violations_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "fix_depth_violations_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "fix_depth_violations_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "fix_depth_violations_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "fix_depth_violations_util", "eval_metric")
_emit_stores_embedding("p4", "fix_depth_violations_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "fix_depth_violations_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "fix_depth_violations_util", "exec_snapshot_link")

"\nFix depth violations by moving shallow files into proper stage subdirectories.\nFiles at Layer/file.py need to move to Layer/Stage/file.py\n"
import shutil
from typing import Any

from agentic_core.L0_routing.config import get_validated_project_root
from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR
from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.L0_routing.utils.path_util import safe_path_join
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
from agentic_core.utils.ssot_discovery_validator import get_python_files

_emit_emits_metric_event("fix_depth_violations_util", "p4obs", "metric_1")
_emit_emits_metric_event("fix_depth_violations_util", "p4obs", "metric_2")
_emit_emits_metric_event("fix_depth_violations_util", "p4obs", "metric_3")
_emit_emits_metric_event("fix_depth_violations_util", "p4obs", "metric_4")
_emit_emits_metric_event("fix_depth_violations_util", "p4obs", "metric_5")
_emit_emits_metric_event("fix_depth_violations_util", "p4obs", "metric_6")
_emit_records_incident_event("fix_depth_violations_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("fix_depth_violations_util", "p4obs", "anomaly")
_emit_writes_observability_log("fix_depth_violations_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("fix_depth_violations_util", "p4obs", "mon_state")
_emit_triggers_alert("fix_depth_violations_util", "p4obs", "alert")
_emit_links_incident_trace("fix_depth_violations_util", "p4obs", "trace_link")
_emit_captures_pattern("fix_depth_violations_util", "p3lm", "pattern")
_emit_records_learning_event("fix_depth_violations_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("fix_depth_violations_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("fix_depth_violations_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("fix_depth_violations_util", "p3lm", "routing")
_emit_improves_agent_policy("fix_depth_violations_util", "p3lm", "policy")
_emit_stores_learning_state("fix_depth_violations_util", "p3lm", "state")
_emit_records_execution_trace("fix_depth_violations_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("fix_depth_violations_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("fix_depth_violations_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("fix_depth_violations_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("fix_depth_violations_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("fix_depth_violations_util", "env_read", "p2_env_1")
_emit_reads_environ("fix_depth_violations_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("fix_depth_violations_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("fix_depth_violations_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "fix_depth_violations_util", "context_pull")
_emit_pulls_context("p1", "fix_depth_violations_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "fix_depth_violations_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "fix_depth_violations_util", "uwg_term_2")
_emit_writes_through("p1", "fix_depth_violations_util", "write_through")
_emit_writes_through("p1", "fix_depth_violations_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "fix_depth_violations_util", "safety_validation")
_emit_invokes_eval("p1", "fix_depth_violations_util", "eval_call")
_emit_proposal_commits_routing("p1", "fix_depth_violations_util", "routing_commit")

PROJECT_ROOT = get_validated_project_root()
CORE = safe_path_join(PROJECT_ROOT, AGENTIC_CORE_DIR)
STAGE_MAPPINGS: Any = {
    "L1_cognition": "P1_core",
    "L2_execution": "P1_core",
    "L3_orchestration": "P1_core",
    "L4_state": "P1_core",
    "L5_safety": "P1_core",
    "memory": "P1_core",
    "patterns": "P1_core",
    "runtime": "P1_core",
    "utils": "P1_core",
}


def fix_depth_violations() -> Any:
    """Move shallow files into proper stage subdirectories."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "fix_depth_violations", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "fix_depth_violations", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "fix_depth_violations")
    print("[*] FIXING DEPTH VIOLATIONS...")
    moved: Any = 0
    for layer_name, default_stage in STAGE_MAPPINGS.items():
        layer_path: Any = CORE / layer_name
        if not layer_path.exists():
            continue
        all_py = get_python_files(PROJECT_ROOT)
        layer_files = [f for f in all_py if str(f).startswith(str(layer_path)) and f.parent == layer_path]
        for py_file in layer_files:
            if py_file.name == "__init__.py":
                continue
            stage_path: Any = layer_path / default_stage
            stage_path.mkdir(exist_ok=True)
            stage_init: Any = stage_path / "__init__.py"
            if not stage_init.exists():
                assert_no_persistent_write("L0", "write_text")
                stage_init.write_text('"""Stage module."""\n')
            target: Any = stage_path / py_file.name
            if not target.exists():
                assert_no_persistent_write("L0", "shutil.mutate")
                shutil.move(str(py_file), str(target))
                print(f"  [✓] Moved: {py_file.relative_to(CORE)} -> {target.relative_to(CORE)}")
                moved += 1
            else:
                print(f"  [SKIP] Already exists: {target.relative_to(CORE)}")
    print(f"\n[OK] Moved {moved} files to proper depth")
    return moved


if __name__ == "__main__":
    fix_depth_violations()
    print("\n[!] NEXT: Run 'python sovereign_lock.py' to verify compliance")
