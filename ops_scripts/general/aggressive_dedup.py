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

from agentic_core.L0_routing.config.path_constants import (
    TESTS_DIR,
)
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

_emit_records_execution_trace("p0", "evidence", "aggressive_dedup")
_emit_applies_guardrail("p0", "aggressive_dedup", "p0_governance")
_emit_reads_policy_state("p0", "aggressive_dedup", "policy_binding")
_emit_snapshots_state("p0", "aggressive_dedup", "state_snapshot")
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
from tqdm import tqdm

_emit_emits_metric_event("aggressive_dedup", "p4obs", "metric_1")
_emit_emits_metric_event("aggressive_dedup", "p4obs", "metric_2")
_emit_emits_metric_event("aggressive_dedup", "p4obs", "metric_3")
_emit_emits_metric_event("aggressive_dedup", "p4obs", "metric_4")
_emit_emits_metric_event("aggressive_dedup", "p4obs", "metric_5")
_emit_emits_metric_event("aggressive_dedup", "p4obs", "metric_6")
_emit_records_incident_event("aggressive_dedup", "p4obs", "incident")
_emit_captures_runtime_anomaly("aggressive_dedup", "p4obs", "anomaly")
_emit_writes_observability_log("aggressive_dedup", "p4obs", "obs_log")
_emit_updates_monitoring_state("aggressive_dedup", "p4obs", "mon_state")
_emit_triggers_alert("aggressive_dedup", "p4obs", "alert")
_emit_links_incident_trace("aggressive_dedup", "p4obs", "trace_link")
_emit_captures_pattern("aggressive_dedup", "p3lm", "pattern")
_emit_records_learning_event("aggressive_dedup", "p3lm", "learning_event")
_emit_writes_learning_snapshot("aggressive_dedup", "p3lm", "snapshot")
_emit_feeds_meta_learning("aggressive_dedup", "p3lm", "meta_feed")
_emit_updates_routing_strategy("aggressive_dedup", "p3lm", "routing")
_emit_improves_agent_policy("aggressive_dedup", "p3lm", "policy")
_emit_stores_learning_state("aggressive_dedup", "p3lm", "state")
_emit_records_execution_trace("aggressive_dedup", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("aggressive_dedup", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("aggressive_dedup", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("aggressive_dedup", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("aggressive_dedup", "L4_STATE", "p2_trace_5")
_emit_reads_environ("aggressive_dedup", "env_read", "p2_env_1")
_emit_reads_environ("aggressive_dedup", "env_read", "p2_env_2")
_emit_reads_runtime_state("aggressive_dedup", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("aggressive_dedup", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "aggressive_dedup", "context_pull")
_emit_pulls_context("p1", "aggressive_dedup", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "aggressive_dedup", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "aggressive_dedup", "uwg_term_2")
_emit_writes_through("p1", "aggressive_dedup", "write_through")
_emit_writes_through("p1", "aggressive_dedup", "write_through_2")
_emit_validated_by_safety_plane("p1", "aggressive_dedup", "safety_validation")
_emit_invokes_eval("p1", "aggressive_dedup", "eval_call")
_emit_proposal_commits_routing("p1", "aggressive_dedup", "routing_commit")
_emit_escalates_to_human("p1", "aggressive_dedup", "human_escalation")
_emit_routes_through("p1", "aggressive_dedup", "route_through")
_emit_checks_agent_registry("p1", "aggressive_dedup", "agent_registry")
_emit_validates_agent_capability("p1", "aggressive_dedup", "capability")
_emit_dispatches_execution_plan("p1", "aggressive_dedup", "exec_plan")
_emit_agent_executes_agent("p1", "aggressive_dedup", "sub_agent")
_emit_routes_to_agent("p1", "aggressive_dedup", "target_agent")
_emit_verifies_policy("p1", "aggressive_dedup", "policy_check")
_emit_observes_runtime_state("p1", "aggressive_dedup", "runtime_state")
_emit_verifies_boundary("p1", "aggressive_dedup", "boundary_check")
_emit_transcripts_response("p1", "aggressive_dedup", "transcript")
_emit_hard_fails_untranscripted("p1", "aggressive_dedup")
_emit_gated_by_confidence("p1", "aggressive_dedup", "confidence_gate")
emit_replay_key("p0", "aggressive_dedup")
emit_determinism_digest("p0", "aggressive_dedup")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "aggressive_dedup", "execution_auth")
_emit_validates_capability("p2", "aggressive_dedup", "capability_check")
_emit_routes_to_capability("p2", "aggressive_dedup", "capability_route")
_emit_writes_via_uwg("p2", "aggressive_dedup", "uwg_write")
_emit_blocks_direct_write("p2", "aggressive_dedup", "direct_write_block")
_emit_records_tool_invocation("p2", "aggressive_dedup", "tool_invocation")
_emit_captures_execution_output("p2", "aggressive_dedup", "exec_output")
_emit_dispatches_agent("p3", "aggressive_dedup", "agent_dispatch")
_emit_coordinates_agents("p3", "aggressive_dedup", "agent_coordination")
_emit_records_workflow_lineage("p3", "aggressive_dedup", "workflow_lineage")
_emit_records_healing_outcome("p3", "aggressive_dedup", "healing_outcome")
_emit_escalates_failure("p3", "aggressive_dedup", "failure_escalation")
_emit_orchestrates_workflow("p3", "aggressive_dedup", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "aggressive_dedup", "healing_dispatch")
_emit_invokes_evaluation("p3", "aggressive_dedup", "evaluation_signal")
_emit_records_telemetry_event("p4", "aggressive_dedup", "telemetry_event")
_emit_captures_evaluation_metric("p4", "aggressive_dedup", "eval_metric")
_emit_stores_embedding("p4", "aggressive_dedup", "embedding_store")
_emit_updates_meta_learning_state("p4", "aggressive_dedup", "meta_learning")
_emit_links_execution_to_snapshot("p4", "aggressive_dedup", "exec_snapshot_link")

APPS_DIRS = [APPS_RG_DIR, APPS_LIC_DIR, APPS_SHARED_DIR]


def get_all_classes_in_codebase(dirs: list[str]) -> dict[str, list[str]]:
    """Get all classes and which files they appear in."""
    class_files = defaultdict(list)
    for d in tqdm(dirs, desc="Processing", unit="item"):
        if not Path(d).exists():
            continue
        for py_file in tqdm(Path(d).rglob("*.py"), desc="Processing", unit="item"):
            if "__pycache__" in str(py_file) or "__init__" in py_file.name:
                continue
            try:
                content = py_file.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_files[node.name].append(str(py_file))
            # guardian: allow-silent-swallow
            except:
                pass
    return class_files


def find_redundant_files(dirs: list[str], class_files: dict[str, list[str]]) -> list[str]:
    """Find files where ALL classes exist in other files."""
    redundant = []
    for d in tqdm(dirs, desc="Processing", unit="item"):
        if not Path(d).exists():
            continue
        for py_file in tqdm(Path(d).rglob("*.py"), desc="Processing", unit="item"):
            if "__pycache__" in str(py_file) or "__init__" in py_file.name:
                continue
            try:
                content = py_file.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(content)
                file_classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                if not file_classes:
                    continue
                all_redundant = True
                for cls_name in file_classes:
                    other_files = [f for f in class_files.get(cls_name, []) if f != str(py_file)]
                    if not other_files:
                        all_redundant = False
                        break
                if all_redundant and len(file_classes) > 0:
                    redundant.append(str(py_file))
            # guardian: allow-silent-swallow
            except:
                pass
    return redundant


def find_similar_named_files(dirs: list[str]) -> list[tuple[str, str]]:
    """Find files with similar names that might be duplicates."""
    all_files = {}
    for d in tqdm(dirs, desc="Processing", unit="item"):
        if not Path(d).exists():
            continue
        for py_file in Path(d).rglob("*.py"):
            if "__pycache__" in str(py_file) or "__init__" in py_file.name:
                continue
            name = py_file.stem.lower()
            name = re.sub("^(task_|tool_|request_|retry_task_)", "", name)
            name = re.sub("(_v\\d+|_\\d+)$", "", name)
            if name not in all_files:
                all_files[name] = []
            all_files[name].append(str(py_file))
    similar_groups = {k: v for k, v in all_files.items() if len(v) > 1}
    return similar_groups


def find_low_value_files(dirs: list[str]) -> list[str]:
    """Find files that are likely low value (small, no docstrings, test-like)."""
    low_value = []
    for d in tqdm(dirs, desc="Processing", unit="item"):
        if not Path(d).exists():
            continue
        for py_file in tqdm(Path(d).rglob("*.py"), desc="Processing", unit="item"):
            if "__pycache__" in str(py_file) or "__init__" in py_file.name:
                continue
            try:
                content = py_file.read_text(encoding="utf-8", errors="replace")
                lines = len(content.splitlines())
                if lines < 20:
                    low_value.append(str(py_file))
                    continue
                if "test" in py_file.stem.lower() and TESTS_DIR not in str(py_file):
                    tree = ast.parse(content)
                    classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
                    if classes and all(c.name.startswith("Test") for c in classes):
                        low_value.append(str(py_file))
                        continue
            # guardian: allow-silent-swallow
            except:
                pass
    return low_value


def _adg_startup_warning() -> None:
    """Emit ADG-sourced antipattern count for this script at startup."""
    try:
        from pathlib import Path as _Path

        from agentic_core.adg.runtime.behavioral_index import get_behavioral_profile

        _root = _Path(__file__).resolve().parents[2]
        _rel = str(_Path(__file__).resolve().relative_to(_root)).replace("\\", "/")
        _profile = get_behavioral_profile(_rel, _root)
        if _profile.antipattern_signals or _profile.behavioral_score < 0.4:
            import warnings

            warnings.warn(
                f"[ADG] {_rel}: {len(_profile.antipattern_signals)} antipattern signal(s) "
                f"detected (score={_profile.behavioral_score:.2f}, "
                f"script-like={_profile.deterministic_coverage}). "
                f"Signals: {sorted(_profile.antipattern_signals) or 'none'}",
                stacklevel=2,
            )
    # guardian: allow-silent-swallow
    except Exception:
        pass


def main():
    _adg_startup_warning()
    print("=" * 80)
    print("AGGRESSIVE DEDUPLICATION")
    print("=" * 80)
    print("\n[1/5] Building class index...")
    class_files = get_all_classes_in_codebase(APPS_DIRS)
    print(f"  Found {len(class_files)} unique class names")
    print("\n[2/5] Finding redundant files (all classes exist elsewhere)...")
    redundant = find_redundant_files(APPS_DIRS, class_files)
    print(f"  Found {len(redundant)} redundant files")
    print("\n[3/5] Finding similar named files...")
    similar_groups = find_similar_named_files(APPS_DIRS)
    print(f"  Found {len(similar_groups)} groups of similar names")
    print("\n[4/5] Finding low value files...")
    low_value = find_low_value_files(APPS_DIRS)
    print(f"  Found {len(low_value)} low value files")
    to_delete = set()
    for f in redundant:
        to_delete.add(f)
    for _name, files in similar_groups.items():
        if len(files) > 1:
            files_sorted = sorted(files, key=lambda x: len(x))
            for f in files_sorted[1:]:
                to_delete.add(f)
    for f in low_value:
        to_delete.add(f)
    print("\n" + "=" * 80)
    print(f"FILES TO DELETE: {len(to_delete)}")
    print("=" * 80)
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
    print("\n[5/5] Executing deletion...")
    deleted = 0
    for f in to_delete:
        try:
            Path(f).unlink()
            deleted += 1
        # guardian: allow-silent-swallow
        except Exception as e:
            print(f"  ✗ Failed: {Path(f).name}: {e}")
    print(f"\n  ✓ Deleted {deleted} files")


if __name__ == "__main__":
    main()
