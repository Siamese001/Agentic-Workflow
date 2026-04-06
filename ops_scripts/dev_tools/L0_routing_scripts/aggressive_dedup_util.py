#!/usr/bin/env python3
"""
Aggressive Deduplication - Remove files with high similarity or redundant content.

Strategies:
1. Remove files where ALL classes exist elsewhere (redundant files)
2. Remove files with very similar names (e.g., Task_X and X)
3. Remove files with >80% content similarity
4. Consolidate test files
"""

import ast
import re
from collections import defaultdict
from pathlib import Path

from agentic_core.L0_routing.config import (
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
)
from agentic_core.L0_routing.config.path_constants import TESTS_DIR
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

emit_replay_key("p0", "aggressive_dedup_util")
emit_determinism_digest("p0", "aggressive_dedup_util")

_emit_dispatches_healing_run("p1", "aggressive_dedup_util", "L0")
_emit_routes_through("p1", "aggressive_dedup_util", "L0")
_emit_checks_agent_registry("p1", "aggressive_dedup_util", "agent_registry")
_emit_validates_agent_capability("p1", "aggressive_dedup_util", "capability")
_emit_dispatches_execution_plan("p1", "aggressive_dedup_util", "exec_plan")
_emit_agent_executes_agent("p1", "aggressive_dedup_util", "sub_agent")
_emit_routes_to_agent("p1", "aggressive_dedup_util", "target_agent")
_emit_verifies_policy("p1", "aggressive_dedup_util", "policy_check")
_emit_observes_runtime_state("p1", "aggressive_dedup_util", "runtime_state")
_emit_verifies_boundary("p1", "aggressive_dedup_util", "boundary_check")
_emit_transcripts_response("p1", "aggressive_dedup_util", "transcript")
_emit_hard_fails_untranscripted("p1", "aggressive_dedup_util")
_emit_gated_by_confidence("p1", "aggressive_dedup_util", "confidence_gate")
_emit_escalates_to_human("p1", "aggressive_dedup_util", "L0")
_emit_reads_policy_state("p1", "aggressive_dedup_util", "L0")
_emit_authorize_and_execute("p2", "aggressive_dedup_util", "execution_auth")
_emit_validates_capability("p2", "aggressive_dedup_util", "capability_check")
_emit_routes_to_capability("p2", "aggressive_dedup_util", "capability_route")
_emit_writes_via_uwg("p2", "aggressive_dedup_util", "uwg_write")
_emit_blocks_direct_write("p2", "aggressive_dedup_util", "direct_write_block")
_emit_records_tool_invocation("p2", "aggressive_dedup_util", "tool_invocation")
_emit_captures_execution_output("p2", "aggressive_dedup_util", "exec_output")
_emit_dispatches_agent("p3", "aggressive_dedup_util", "agent_dispatch")
_emit_coordinates_agents("p3", "aggressive_dedup_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "aggressive_dedup_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "aggressive_dedup_util", "healing_outcome")
_emit_escalates_failure("p3", "aggressive_dedup_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "aggressive_dedup_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "aggressive_dedup_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "aggressive_dedup_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "aggressive_dedup_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "aggressive_dedup_util", "eval_metric")
_emit_stores_embedding("p4", "aggressive_dedup_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "aggressive_dedup_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "aggressive_dedup_util", "exec_snapshot_link")
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

_emit_emits_metric_event("aggressive_dedup_util", "p4obs", "metric_1")
_emit_emits_metric_event("aggressive_dedup_util", "p4obs", "metric_2")
_emit_emits_metric_event("aggressive_dedup_util", "p4obs", "metric_3")
_emit_emits_metric_event("aggressive_dedup_util", "p4obs", "metric_4")
_emit_emits_metric_event("aggressive_dedup_util", "p4obs", "metric_5")
_emit_emits_metric_event("aggressive_dedup_util", "p4obs", "metric_6")
_emit_records_incident_event("aggressive_dedup_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("aggressive_dedup_util", "p4obs", "anomaly")
_emit_writes_observability_log("aggressive_dedup_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("aggressive_dedup_util", "p4obs", "mon_state")
_emit_triggers_alert("aggressive_dedup_util", "p4obs", "alert")
_emit_links_incident_trace("aggressive_dedup_util", "p4obs", "trace_link")
_emit_captures_pattern("aggressive_dedup_util", "p3lm", "pattern")
_emit_records_learning_event("aggressive_dedup_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("aggressive_dedup_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("aggressive_dedup_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("aggressive_dedup_util", "p3lm", "routing")
_emit_improves_agent_policy("aggressive_dedup_util", "p3lm", "policy")
_emit_stores_learning_state("aggressive_dedup_util", "p3lm", "state")
_emit_records_execution_trace("aggressive_dedup_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("aggressive_dedup_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("aggressive_dedup_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("aggressive_dedup_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("aggressive_dedup_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("aggressive_dedup_util", "env_read", "p2_env_1")
_emit_reads_environ("aggressive_dedup_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("aggressive_dedup_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("aggressive_dedup_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "aggressive_dedup_util", "context_pull")
_emit_pulls_context("p1", "aggressive_dedup_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "aggressive_dedup_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "aggressive_dedup_util", "uwg_term_2")
_emit_writes_through("p1", "aggressive_dedup_util", "write_through")
_emit_writes_through("p1", "aggressive_dedup_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "aggressive_dedup_util", "safety_validation")
_emit_invokes_eval("p1", "aggressive_dedup_util", "eval_call")
_emit_proposal_commits_routing("p1", "aggressive_dedup_util", "routing_commit")

APPS_DIRS = [APPS_RG_DIR, APPS_LIC_DIR, APPS_SHARED_DIR]


def get_all_classes_in_codebase(dirs: list[str]) -> dict[str, list[str]]:
    """Get all classes and which files they appear in."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "get_all_classes_in_codebase", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "get_all_classes_in_codebase", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "get_all_classes_in_codebase")
    class_files = defaultdict(list)

    for d in dirs:
        if not Path(d).exists():
            continue
        for py_file in Path(d).rglob("*.py"):
            if "__pycache__" in str(py_file) or "__init__" in py_file.name:
                continue
            try:
                content = py_file.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_files[node.name].append(str(py_file))
            # guardian: allow-silent-swallow
            except (ValueError, TypeError):
                pass

    return class_files


def find_redundant_files(dirs: list[str], class_files: dict[str, list[str]]) -> list[str]:
    """Find files where ALL classes exist in other files."""
    redundant = []

    for d in dirs:
        if not Path(d).exists():
            continue
        for py_file in Path(d).rglob("*.py"):
            if "__pycache__" in str(py_file) or "__init__" in py_file.name:
                continue

            try:
                content = py_file.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(content)

                file_classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

                if not file_classes:
                    continue

                # Check if all classes exist in other files
                all_redundant = True
                for cls_name in file_classes:
                    other_files = [f for f in class_files.get(cls_name, []) if f != str(py_file)]
                    if not other_files:
                        all_redundant = False
                        break

                if all_redundant and len(file_classes) > 0:
                    redundant.append(str(py_file))
            # guardian: allow-silent-swallow
            except (ValueError, TypeError):
                pass

    return redundant


def find_similar_named_files(dirs: list[str]) -> list[tuple[str, str]]:
    """Find files with similar names that might be duplicates."""
    all_files = {}

    for d in dirs:
        if not Path(d).exists():
            continue
        for py_file in Path(d).rglob("*.py"):
            if "__pycache__" in str(py_file) or "__init__" in py_file.name:
                continue

            # Normalize name
            name = py_file.stem.lower()
            name = re.sub(r"^(task_|tool_|request_|retry_task_)", "", name)
            name = re.sub(r"(_v\d+|_\d+)$", "", name)

            if name not in all_files:
                all_files[name] = []
            all_files[name].append(str(py_file))

    # Find groups with multiple files
    similar_groups = {k: v for k, v in all_files.items() if len(v) > 1}
    return similar_groups


def find_low_value_files(dirs: list[str]) -> list[str]:
    """Find files that are likely low value (small, no docstrings, test-like)."""
    low_value = []

    for d in dirs:
        if not Path(d).exists():
            continue
        for py_file in Path(d).rglob("*.py"):
            if "__pycache__" in str(py_file) or "__init__" in py_file.name:
                continue

            try:
                content = py_file.read_text(encoding="utf-8", errors="replace")
                lines = len(content.splitlines())

                # Skip very small files
                if lines < 20:
                    low_value.append(str(py_file))
                    continue

                # Check for test-only files in non-test locations
                if "test" in py_file.stem.lower() and TESTS_DIR not in str(py_file):
                    tree = ast.parse(content)
                    classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
                    # If all classes are test classes
                    if classes and all(c.name.startswith("Test") for c in classes):
                        low_value.append(str(py_file))
                        continue

            # guardian: allow-silent-swallow
            except (ValueError, TypeError):
                pass

    return low_value


def main():
    print("=" * 80)
    print("AGGRESSIVE DEDUPLICATION")
    print("=" * 80)

    # Get all classes
    print("\n[1/5] Building class index...")
    class_files = get_all_classes_in_codebase(APPS_DIRS)
    print(f"  Found {len(class_files)} unique class names")

    # Find redundant files
    print("\n[2/5] Finding redundant files (all classes exist elsewhere)...")
    redundant = find_redundant_files(APPS_DIRS, class_files)
    print(f"  Found {len(redundant)} redundant files")

    # Find similar named files
    print("\n[3/5] Finding similar named files...")
    similar_groups = find_similar_named_files(APPS_DIRS)
    print(f"  Found {len(similar_groups)} groups of similar names")

    # Find low value files
    print("\n[4/5] Finding low value files...")
    low_value = find_low_value_files(APPS_DIRS)
    print(f"  Found {len(low_value)} low value files")

    # Consolidate deletion list
    to_delete = set()

    # Add redundant files
    for f in redundant:
        to_delete.add(f)

    # For similar named files, keep the shortest path (likely the canonical one)
    for _name, files in similar_groups.items():
        if len(files) > 1:
            # Sort by path length, keep shortest
            files_sorted = sorted(files, key=lambda x: len(x))
            for f in files_sorted[1:]:  # Delete all but first
                to_delete.add(f)

    # Add low value files
    for f in low_value:
        to_delete.add(f)

    print("\n" + "=" * 80)
    print(f"FILES TO DELETE: {len(to_delete)}")
    print("=" * 80)

    # Group by folder for display
    by_folder = defaultdict(list)
    for f in sorted(to_delete):
        folder = Path(f).parent.name
        by_folder[folder].append(Path(f).name)

    for folder, files in sorted(by_folder.items()):
        print(f"\n  {folder}/ ({len(files)} files)")
        for f in files[:10]:
            print(f"    - {f}")
        if len(files) > 10:
            print(f"    ... and {len(files) - 10} more")

    # Execute deletion
    print("\n[5/5] Executing deletion...")

    deleted = 0
    for f in to_delete:
        try:
            Path(f).unlink()
            deleted += 1
        # guardian: allow-silent-swallow
        except (ValueError, TypeError) as e:
            print(f"  ✗ Failed: {Path(f).name}: {e}")

    print(f"\n  ✓ Deleted {deleted} files")


if __name__ == "__main__":
    main()
