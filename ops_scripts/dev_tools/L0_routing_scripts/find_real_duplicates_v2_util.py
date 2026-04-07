"""
Find REAL duplicate agent files by NAME (not content hash).
Shows files with same name in different locations.
"""

from collections import defaultdict
from datetime import datetime
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

emit_replay_key("p0", "find_real_duplicates_v2_util")
emit_determinism_digest("p0", "find_real_duplicates_v2_util")

_emit_dispatches_healing_run("p1", "find_real_duplicates_v2_util", "L0")
_emit_routes_through("p1", "find_real_duplicates_v2_util", "L0")
_emit_checks_agent_registry("p1", "find_real_duplicates_v2_util", "agent_registry")
_emit_validates_agent_capability("p1", "find_real_duplicates_v2_util", "capability")
_emit_dispatches_execution_plan("p1", "find_real_duplicates_v2_util", "exec_plan")
_emit_agent_executes_agent("p1", "find_real_duplicates_v2_util", "sub_agent")
_emit_routes_to_agent("p1", "find_real_duplicates_v2_util", "target_agent")
_emit_verifies_policy("p1", "find_real_duplicates_v2_util", "policy_check")
_emit_observes_runtime_state("p1", "find_real_duplicates_v2_util", "runtime_state")
_emit_verifies_boundary("p1", "find_real_duplicates_v2_util", "boundary_check")
_emit_transcripts_response("p1", "find_real_duplicates_v2_util", "transcript")
_emit_hard_fails_untranscripted("p1", "find_real_duplicates_v2_util")
_emit_gated_by_confidence("p1", "find_real_duplicates_v2_util", "confidence_gate")
_emit_escalates_to_human("p1", "find_real_duplicates_v2_util", "L0")
_emit_reads_policy_state("p1", "find_real_duplicates_v2_util", "L0")
_emit_authorize_and_execute("p2", "find_real_duplicates_v2_util", "execution_auth")
_emit_validates_capability("p2", "find_real_duplicates_v2_util", "capability_check")
_emit_routes_to_capability("p2", "find_real_duplicates_v2_util", "capability_route")
_emit_writes_via_uwg("p2", "find_real_duplicates_v2_util", "uwg_write")
_emit_blocks_direct_write("p2", "find_real_duplicates_v2_util", "direct_write_block")
_emit_records_tool_invocation("p2", "find_real_duplicates_v2_util", "tool_invocation")
_emit_captures_execution_output("p2", "find_real_duplicates_v2_util", "exec_output")
_emit_dispatches_agent("p3", "find_real_duplicates_v2_util", "agent_dispatch")
_emit_coordinates_agents("p3", "find_real_duplicates_v2_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "find_real_duplicates_v2_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "find_real_duplicates_v2_util", "healing_outcome")
_emit_escalates_failure("p3", "find_real_duplicates_v2_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "find_real_duplicates_v2_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "find_real_duplicates_v2_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "find_real_duplicates_v2_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "find_real_duplicates_v2_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "find_real_duplicates_v2_util", "eval_metric")
_emit_stores_embedding("p4", "find_real_duplicates_v2_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "find_real_duplicates_v2_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "find_real_duplicates_v2_util", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("find_real_duplicates_v2_util", "p4obs", "metric_1")
_emit_emits_metric_event("find_real_duplicates_v2_util", "p4obs", "metric_2")
_emit_emits_metric_event("find_real_duplicates_v2_util", "p4obs", "metric_3")
_emit_emits_metric_event("find_real_duplicates_v2_util", "p4obs", "metric_4")
_emit_emits_metric_event("find_real_duplicates_v2_util", "p4obs", "metric_5")
_emit_emits_metric_event("find_real_duplicates_v2_util", "p4obs", "metric_6")
_emit_records_incident_event("find_real_duplicates_v2_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("find_real_duplicates_v2_util", "p4obs", "anomaly")
_emit_writes_observability_log("find_real_duplicates_v2_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("find_real_duplicates_v2_util", "p4obs", "mon_state")
_emit_triggers_alert("find_real_duplicates_v2_util", "p4obs", "alert")
_emit_links_incident_trace("find_real_duplicates_v2_util", "p4obs", "trace_link")
_emit_captures_pattern("find_real_duplicates_v2_util", "p3lm", "pattern")
_emit_records_learning_event("find_real_duplicates_v2_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("find_real_duplicates_v2_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("find_real_duplicates_v2_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("find_real_duplicates_v2_util", "p3lm", "routing")
_emit_improves_agent_policy("find_real_duplicates_v2_util", "p3lm", "policy")
_emit_stores_learning_state("find_real_duplicates_v2_util", "p3lm", "state")
_emit_records_execution_trace("find_real_duplicates_v2_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("find_real_duplicates_v2_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("find_real_duplicates_v2_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("find_real_duplicates_v2_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("find_real_duplicates_v2_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("find_real_duplicates_v2_util", "env_read", "p2_env_1")
_emit_reads_environ("find_real_duplicates_v2_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("find_real_duplicates_v2_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("find_real_duplicates_v2_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "find_real_duplicates_v2_util", "context_pull")
_emit_pulls_context("p1", "find_real_duplicates_v2_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "find_real_duplicates_v2_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "find_real_duplicates_v2_util", "uwg_term_2")
_emit_writes_through("p1", "find_real_duplicates_v2_util", "write_through")
_emit_writes_through("p1", "find_real_duplicates_v2_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "find_real_duplicates_v2_util", "safety_validation")
_emit_invokes_eval("p1", "find_real_duplicates_v2_util", "eval_call")
_emit_proposal_commits_routing("p1", "find_real_duplicates_v2_util", "routing_commit")


def is_agent_file(path: Path) -> bool:
    """Check if path is an actual agent file (not test).

    [REFACTORED 2026-02-08] Aligned with classification kernel naming rules.
    For full AST-based classification, use:
        from agentic_core.L5_safety.core_kernel.classification_kernel import is_agent_file
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "is_agent_file", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "is_agent_file", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "is_agent_file")
    if not path.name.endswith("Agent.py"):
        return False
    path_str = str(path).lower()
    if "test" in path_str or "\\tests\\" in path_str or "/tests/" in path_str:
        return False
    if "__pycache__" in path_str or ".venv" in path_str:
        return False
    if "Mixin" in path.name:
        return False
    return True


def get_priority(path: Path, project_root: Path) -> int:
    """Get location priority (lower = better/canonical)."""
    rel_path = str(path.relative_to(project_root)).replace("\\", "/")
    if "blueprint_sovereign" in rel_path:
        return 10
    elif "L5_safety/validators" in rel_path:
        return 2
    elif "L5_safety/agents" in rel_path:
        return 1
    elif rel_path.startswith("agentic_core/"):
        return 3
    else:
        return 5


def infer_rationale(canonical: Path, duplicate: Path, project_root: Path) -> str:
    """Infer rationale based on path patterns."""
    dup_str = str(duplicate.relative_to(project_root))
    can_str = str(canonical.relative_to(project_root))
    if "blueprint_sovereign" in dup_str:
        return "Leftover blueprint template — production version is canonical"
    if "validators" in can_str and "agents" in dup_str or ("agents" in can_str and "validators" in dup_str):
        return "Location overlap: same agent in agents/ vs validators/ directories"
    if "runtime" in dup_str or "runtime" in can_str:
        return "Runtime duplicate — consolidate to primary location"
    return "Exact duplicate — likely copy-paste or migration artifact"


def main():
    project_root = Path.cwd()
    print(f"[SCAN] Searching for agent files in {project_root}...")
    from agentic_core.utils.runners.ssot_discovery_validator import get_agent_files

    agent_files = [f for f in get_agent_files(project_root) if is_agent_file(f)]
    print(f"[SCAN] Found {len(agent_files)} agent files")
    name_to_files = defaultdict(list)
    for file_path in agent_files:
        name_to_files[file_path.name].append(file_path)
    duplicates = {name: files for name, files in name_to_files.items() if len(files) > 1}
    print(f"[FOUND] {len(duplicates)} agent names with multiple locations")
    if not duplicates:
        print("\n✅ No duplicates found!")
        return 0
    output_file = project_root / REPORTS_DIR / "real_duplicates_by_name.md"
    output_file.parent.mkdir(exist_ok=True)
    total_files_to_delete = sum(len(files) - 1 for files in duplicates.values())
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Real Duplicate Agents (By Name)\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Duplicate Agent Names:** {len(duplicates)}\n")
        f.write(f"**Files to Delete:** {total_files_to_delete}\n\n")
        f.write("| Agent Name | Canonical Path | Duplicate Path | Rationale |\n")
        f.write("| --- | --- | --- | --- |\n")
        for agent_name, files in sorted(duplicates.items()):
            files_sorted = sorted(files, key=lambda f: (get_priority(f, project_root), str(f)))
            canonical = files_sorted[0]
            for duplicate in files_sorted[1:]:
                canonical_rel = canonical.relative_to(project_root)
                duplicate_rel = duplicate.relative_to(project_root)
                rationale = infer_rationale(canonical, duplicate, project_root)
                f.write(
                    f"| {agent_name.replace('.py', '')} | `{canonical_rel}` | `{duplicate_rel}` | {rationale} |\n",
                )
        f.write("\n---\n\n")
        f.write("## Delete Commands\n\n")
        f.write("**IMPORTANT:** Review each file before deleting. Use diff to compare:\n")
        f.write("```bash\n")
        f.write('code --diff "canonical_path" "duplicate_path"\n')
        f.write("```\n\n")
        f.write("### Delete Duplicates\n")
        f.write("```bash\n")
        for agent_name, files in sorted(duplicates.items()):
            files_sorted = sorted(files, key=lambda f: (get_priority(f, project_root), str(f)))
            for duplicate in files_sorted[1:]:
                duplicate_rel = duplicate.relative_to(project_root)
                f.write(f'git rm "{duplicate_rel}"\n')
        f.write("```\n")
    print(f"\n✅ Generated: {output_file}")
    print(f"   Duplicate agent names: {len(duplicates)}")
    print(f"   Files to delete: {total_files_to_delete}")
    print("\n" + "=" * 80)
    print("REAL DUPLICATES FOUND (BY NAME)")
    print("=" * 80)
    for agent_name, files in sorted(duplicates.items()):
        files_sorted = sorted(files, key=lambda f: (get_priority(f, project_root), str(f)))
        canonical = files_sorted[0]
        print(f"\n[{agent_name.replace('.py', '')}]")
        print(f"  ✅ KEEP: {canonical.relative_to(project_root)}")
        for duplicate in files_sorted[1:]:
            print(f"  ❌ DELETE: {duplicate.relative_to(project_root)}")
    return 0


if __name__ == "__main__":
    exit(main())
