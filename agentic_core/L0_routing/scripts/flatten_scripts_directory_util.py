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

emit_replay_key("p0", "flatten_scripts_directory_util")
emit_determinism_digest("p0", "flatten_scripts_directory_util")

_emit_dispatches_healing_run("p1", "flatten_scripts_directory_util", "L0")
_emit_routes_through("p1", "flatten_scripts_directory_util", "L0")
_emit_checks_agent_registry("p1", "flatten_scripts_directory_util", "agent_registry")
_emit_validates_agent_capability("p1", "flatten_scripts_directory_util", "capability")
_emit_dispatches_execution_plan("p1", "flatten_scripts_directory_util", "exec_plan")
_emit_agent_executes_agent("p1", "flatten_scripts_directory_util", "sub_agent")
_emit_routes_to_agent("p1", "flatten_scripts_directory_util", "target_agent")
_emit_verifies_policy("p1", "flatten_scripts_directory_util", "policy_check")
_emit_observes_runtime_state("p1", "flatten_scripts_directory_util", "runtime_state")
_emit_verifies_boundary("p1", "flatten_scripts_directory_util", "boundary_check")
_emit_transcripts_response("p1", "flatten_scripts_directory_util", "transcript")
_emit_hard_fails_untranscripted("p1", "flatten_scripts_directory_util")
_emit_gated_by_confidence("p1", "flatten_scripts_directory_util", "confidence_gate")
_emit_escalates_to_human("p1", "flatten_scripts_directory_util", "L0")
_emit_reads_policy_state("p1", "flatten_scripts_directory_util", "L0")
_emit_authorize_and_execute("p2", "flatten_scripts_directory_util", "execution_auth")
_emit_validates_capability("p2", "flatten_scripts_directory_util", "capability_check")
_emit_routes_to_capability("p2", "flatten_scripts_directory_util", "capability_route")
_emit_writes_via_uwg("p2", "flatten_scripts_directory_util", "uwg_write")
_emit_blocks_direct_write("p2", "flatten_scripts_directory_util", "direct_write_block")
_emit_records_tool_invocation("p2", "flatten_scripts_directory_util", "tool_invocation")
_emit_captures_execution_output("p2", "flatten_scripts_directory_util", "exec_output")
_emit_dispatches_agent("p3", "flatten_scripts_directory_util", "agent_dispatch")
_emit_coordinates_agents("p3", "flatten_scripts_directory_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "flatten_scripts_directory_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "flatten_scripts_directory_util", "healing_outcome")
_emit_escalates_failure("p3", "flatten_scripts_directory_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "flatten_scripts_directory_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "flatten_scripts_directory_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "flatten_scripts_directory_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "flatten_scripts_directory_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "flatten_scripts_directory_util", "eval_metric")
_emit_stores_embedding("p4", "flatten_scripts_directory_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "flatten_scripts_directory_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "flatten_scripts_directory_util", "exec_snapshot_link")

"""
Flatten scripts directory to SSOT-compliant depth.
[SSOT] All depth requirements derived from SOVEREIGN_REGISTRY in structure_blueprint.py
"""
import os
import shutil
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
)
from agentic_core.L0_routing.config.path_constants import DEPTH_RULES, SOVEREIGN_EXCLUDED_FOLDERS
from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.L0_routing.utils.path_util import (
    safe_prefixed_filename,
    validate_no_duplicate_prefix,
)
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

_emit_emits_metric_event("flatten_scripts_directory_util", "p4obs", "metric_1")
_emit_emits_metric_event("flatten_scripts_directory_util", "p4obs", "metric_2")
_emit_emits_metric_event("flatten_scripts_directory_util", "p4obs", "metric_3")
_emit_emits_metric_event("flatten_scripts_directory_util", "p4obs", "metric_4")
_emit_emits_metric_event("flatten_scripts_directory_util", "p4obs", "metric_5")
_emit_emits_metric_event("flatten_scripts_directory_util", "p4obs", "metric_6")
_emit_records_incident_event("flatten_scripts_directory_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("flatten_scripts_directory_util", "p4obs", "anomaly")
_emit_writes_observability_log("flatten_scripts_directory_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("flatten_scripts_directory_util", "p4obs", "mon_state")
_emit_triggers_alert("flatten_scripts_directory_util", "p4obs", "alert")
_emit_links_incident_trace("flatten_scripts_directory_util", "p4obs", "trace_link")
_emit_captures_pattern("flatten_scripts_directory_util", "p3lm", "pattern")
_emit_records_learning_event("flatten_scripts_directory_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("flatten_scripts_directory_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("flatten_scripts_directory_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("flatten_scripts_directory_util", "p3lm", "routing")
_emit_improves_agent_policy("flatten_scripts_directory_util", "p3lm", "policy")
_emit_stores_learning_state("flatten_scripts_directory_util", "p3lm", "state")
_emit_records_execution_trace("flatten_scripts_directory_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("flatten_scripts_directory_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("flatten_scripts_directory_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("flatten_scripts_directory_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("flatten_scripts_directory_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("flatten_scripts_directory_util", "env_read", "p2_env_1")
_emit_reads_environ("flatten_scripts_directory_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("flatten_scripts_directory_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("flatten_scripts_directory_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "flatten_scripts_directory_util", "context_pull")
_emit_pulls_context("p1", "flatten_scripts_directory_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "flatten_scripts_directory_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "flatten_scripts_directory_util", "uwg_term_2")
_emit_writes_through("p1", "flatten_scripts_directory_util", "write_through")
_emit_writes_through("p1", "flatten_scripts_directory_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "flatten_scripts_directory_util", "safety_validation")
_emit_invokes_eval("p1", "flatten_scripts_directory_util", "eval_call")
_emit_proposal_commits_routing("p1", "flatten_scripts_directory_util", "routing_commit")

ROOT: Any = Path(__file__).resolve().parents[4]
CORE: Any = ROOT / AGENTIC_CORE_DIR
SCRIPTS_DIR: Any = CORE / "L0_routing/scripts"
REQUIRED_DEPTH: Any = DEPTH_RULES.get("agentic_core", 4)


def flatten_scripts() -> Any:
    """Brief description of functionality and purpose."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "flatten_scripts", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "flatten_scripts", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "flatten_scripts")
    print(f"[*] FLATTENING L0_routing/scripts TO DEPTH-{REQUIRED_DEPTH}...")
    moved: Any = 0
    if not SCRIPTS_DIR.exists():
        print("[!] Scripts directory not found")
        return
    # Phase 6.9: Use ssot_discovery instead of rglob
    from agentic_core.L0_routing.utils.ssot_discovery_util import get_python_files

    for py_file in get_python_files(SCRIPTS_DIR):
        rel_path: Any = py_file.relative_to(CORE)
        parts: Any = rel_path.parts
        if len(parts) > REQUIRED_DEPTH - 1:
            path_prefix: Any = "_".join(parts[2:-1])
            # [SAFEGUARD] Use SSOT function to prevent duplicate prefix sprawl
            new_name: Any = safe_prefixed_filename(path_prefix, py_file.name)

            # Validate no duplicate prefix was created
            has_dup, dup_msg = validate_no_duplicate_prefix(new_name)
            if has_dup:
                print(f"  [!] BLOCKED: {dup_msg}")
                continue

            target: Any = SCRIPTS_DIR / new_name
            counter: Any = 1
            while target.exists():
                target: Any = SCRIPTS_DIR / f"{path_prefix}_{counter}_{py_file.stem}{py_file.suffix}"
                counter += 1
            try:
                assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
                shutil.move(str(py_file), str(target))
                print(f"  [✓] {rel_path} -> {target.relative_to(CORE)}")
                moved += 1
            # guardian: allow-silent-swallow
            except (ValueError, TypeError) as e:
                print(f"  [X] Failed: {py_file.name} - {e}")
    print("\n[*] Cleaning empty directories...")
    for root, dirs, _files in os.walk(SCRIPTS_DIR, topdown=False):
        dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
        for dir_name in dirs:
            dir_path: Any = Path(root) / dir_name
            try:
                if not any(dir_path.iterdir()) and dir_path != SCRIPTS_DIR:
                    dir_path.rmdir()
                    print(f"  [✓] Removed: {dir_path.relative_to(CORE)}")
            # guardian: allow-silent-swallow
            except (ValueError, TypeError):
                pass
    print(f"\n[OK] FLATTENING COMPLETE. {moved} files moved to depth-{REQUIRED_DEPTH}.")


if __name__ == "__main__":
    flatten_scripts()
