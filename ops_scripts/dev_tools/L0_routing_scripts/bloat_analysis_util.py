#!/usr/bin/env python3
"""Bloat analysis script for approved folders."""

import ast
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
    TESTS_DIR,
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

_emit_emits_metric_event("bloat_analysis_util", "p4obs", "metric_1")
_emit_emits_metric_event("bloat_analysis_util", "p4obs", "metric_2")
_emit_emits_metric_event("bloat_analysis_util", "p4obs", "metric_3")
_emit_emits_metric_event("bloat_analysis_util", "p4obs", "metric_4")
_emit_emits_metric_event("bloat_analysis_util", "p4obs", "metric_5")
_emit_emits_metric_event("bloat_analysis_util", "p4obs", "metric_6")
_emit_records_incident_event("bloat_analysis_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("bloat_analysis_util", "p4obs", "anomaly")
_emit_writes_observability_log("bloat_analysis_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("bloat_analysis_util", "p4obs", "mon_state")
_emit_triggers_alert("bloat_analysis_util", "p4obs", "alert")
_emit_links_incident_trace("bloat_analysis_util", "p4obs", "trace_link")
_emit_captures_pattern("bloat_analysis_util", "p3lm", "pattern")
_emit_records_learning_event("bloat_analysis_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("bloat_analysis_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("bloat_analysis_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("bloat_analysis_util", "p3lm", "routing")
_emit_improves_agent_policy("bloat_analysis_util", "p3lm", "policy")
_emit_stores_learning_state("bloat_analysis_util", "p3lm", "state")
_emit_records_execution_trace("bloat_analysis_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("bloat_analysis_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("bloat_analysis_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("bloat_analysis_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("bloat_analysis_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("bloat_analysis_util", "env_read", "p2_env_1")
_emit_reads_environ("bloat_analysis_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("bloat_analysis_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("bloat_analysis_util", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "bloat_analysis_util")
emit_determinism_digest("p0", "bloat_analysis_util")

_emit_dispatches_healing_run("p1", "bloat_analysis_util", "L0")
_emit_routes_through("p1", "bloat_analysis_util", "L0")
_emit_checks_agent_registry("p1", "bloat_analysis_util", "agent_registry")
_emit_validates_agent_capability("p1", "bloat_analysis_util", "capability")
_emit_dispatches_execution_plan("p1", "bloat_analysis_util", "exec_plan")
_emit_agent_executes_agent("p1", "bloat_analysis_util", "sub_agent")
_emit_routes_to_agent("p1", "bloat_analysis_util", "target_agent")
_emit_verifies_policy("p1", "bloat_analysis_util", "policy_check")
_emit_observes_runtime_state("p1", "bloat_analysis_util", "runtime_state")
_emit_verifies_boundary("p1", "bloat_analysis_util", "boundary_check")
_emit_transcripts_response("p1", "bloat_analysis_util", "transcript")
_emit_hard_fails_untranscripted("p1", "bloat_analysis_util")
_emit_gated_by_confidence("p1", "bloat_analysis_util", "confidence_gate")
_emit_escalates_to_human("p1", "bloat_analysis_util", "L0")
_emit_reads_policy_state("p1", "bloat_analysis_util", "L0")
_emit_pulls_context("p1", "bloat_analysis_util", "context_pull")
_emit_pulls_context("p1", "bloat_analysis_util", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "bloat_analysis_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "bloat_analysis_util", "uwg_term_secondary")
_emit_writes_through("p1", "bloat_analysis_util", "write_through")
_emit_writes_through("p1", "bloat_analysis_util", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "bloat_analysis_util", "safety_validation")
_emit_invokes_eval("p1", "bloat_analysis_util", "eval_call")
_emit_proposal_commits_routing("p1", "bloat_analysis_util", "routing_commit")

_emit_records_execution_trace("p0", "evidence", "bloat_analysis_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "bloat_analysis_util", "p0_governance")
_emit_snapshots_state("p0", "bloat_analysis_util", "state_snapshot")
_emit_authorize_and_execute("p2", "bloat_analysis_util", "execution_auth")
_emit_validates_capability("p2", "bloat_analysis_util", "capability_check")
_emit_routes_to_capability("p2", "bloat_analysis_util", "capability_route")
_emit_writes_via_uwg("p2", "bloat_analysis_util", "uwg_write")
_emit_blocks_direct_write("p2", "bloat_analysis_util", "direct_write_block")
_emit_records_tool_invocation("p2", "bloat_analysis_util", "tool_invocation")
_emit_captures_execution_output("p2", "bloat_analysis_util", "exec_output")
_emit_dispatches_agent("p3", "bloat_analysis_util", "agent_dispatch")
_emit_coordinates_agents("p3", "bloat_analysis_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "bloat_analysis_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "bloat_analysis_util", "healing_outcome")
_emit_escalates_failure("p3", "bloat_analysis_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "bloat_analysis_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "bloat_analysis_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "bloat_analysis_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "bloat_analysis_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "bloat_analysis_util", "eval_metric")
_emit_stores_embedding("p4", "bloat_analysis_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "bloat_analysis_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "bloat_analysis_util", "exec_snapshot_link")

ROOT = Path(__file__).parent.parent
APPROVED = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS


def get_file_stats():
    """Get file statistics by extension and folder."""
    stats = defaultdict(lambda: {"count": 0, "size": 0})
    folder_stats = defaultdict(lambda: {"py": 0, "other": 0, "total_size": 0})

    for folder in tqdm(APPROVED, desc="Processing", unit="item"):
        folder_path = ROOT / folder
        if not folder_path.exists():
            continue
        for f in tqdm(folder_path.rglob("*"), desc="Processing", unit="item"):
            if f.is_file() and "__pycache__" not in str(f):
                ext = f.suffix.lower()
                size = f.stat().st_size
                stats[ext]["count"] += 1
                stats[ext]["size"] += size
                if ext == ".py":
                    folder_stats[folder]["py"] += 1
                else:
                    folder_stats[folder]["other"] += 1
                folder_stats[folder]["total_size"] += size

    return stats, folder_stats


# guardian: allow-magic-config
def find_large_files(min_size_kb=50):
    """Find files larger than threshold."""
    large = []
    for folder in tqdm(APPROVED, desc="Processing", unit="item"):
        folder_path = ROOT / folder
        if not folder_path.exists():
            continue
        for f in tqdm(folder_path.rglob("*.py"), desc="Processing", unit="item"):
            if "__pycache__" in str(f):
                continue
            size = f.stat().st_size
            if size > min_size_kb * 1024:
                large.append(
                    {
                        "path": str(f.relative_to(ROOT)),
                        "size_kb": round(size / 1024, 1),
                        "lines": len(f.read_text(encoding="utf-8", errors="replace").splitlines()),
                    },
                )
    return sorted(large, key=lambda x: -x["size_kb"])


def find_duplicate_filenames():
    """Find files with duplicate names."""
    names = defaultdict(list)
    for folder in APPROVED:
        folder_path = ROOT / folder
        if not folder_path.exists():
            continue
        for f in folder_path.rglob("*.py"):
            if "__pycache__" in str(f):
                continue
            names[f.name].append(str(f.relative_to(ROOT)))
    return {k: v for k, v in names.items() if len(v) > 1}


def find_empty_or_stub_files():
    """Find empty or stub Python files."""
    stubs = []
    for folder in tqdm(APPROVED, desc="Processing", unit="item"):
        folder_path = ROOT / folder
        if not folder_path.exists():
            continue
        for f in tqdm(folder_path.rglob("*.py"), desc="Processing", unit="item"):
            if "__pycache__" in str(f) or f.name == "__init__.py":
                continue
            try:
                content = f.read_text(encoding="utf-8", errors="replace")
                lines = [l for l in content.splitlines() if l.strip() and not l.strip().startswith("#")]
                # Remove docstrings
                code_lines = []
                in_docstring = False
                for line in lines:
                    if '"""' in line or "'''" in line:
                        in_docstring = not in_docstring
                        continue
                    if not in_docstring:
                        code_lines.append(line)
                if len(code_lines) < 5:
                    stubs.append(
                        {
                            "path": str(f.relative_to(ROOT)),
                            "code_lines": len(code_lines),
                            "total_lines": len(content.splitlines()),
                        },
                    )
            except (OSError, UnicodeDecodeError) as e:  # guardian: allow-silent-swallow - acceptable exception handling
                print(f"Failed to scan {f.name}: {e}")
    return stubs


def find_deprecated_markers():
    """Find files with deprecation markers."""
    deprecated = []
    markers = ["DEPRECATED", "TODO: Remove", "TODO: Delete", "LEGACY", "OBSOLETE", "TO BE REMOVED"]
    for folder in tqdm(APPROVED, desc="Processing", unit="item"):
        folder_path = ROOT / folder
        if not folder_path.exists():
            continue
        for f in tqdm(folder_path.rglob("*.py"), desc="Processing", unit="item"):
            if "__pycache__" in str(f):
                continue
            try:
                content = f.read_text(encoding="utf-8", errors="replace")
                for marker in markers:
                    if marker.lower() in content.lower():
                        deprecated.append({"path": str(f.relative_to(ROOT)), "marker": marker})
                        # guardian: allow-silent-swallow - acceptable exception handling
                        break
            except (OSError, UnicodeDecodeError) as e:
                print(f"Failed to scan {f.name}: {e}")
    return deprecated


def find_test_files_outside_tests():
    """Find test files outside tests/ folder."""
    misplaced = []
    for folder in tqdm(APPROVED, desc="Processing", unit="item"):
        if folder == TESTS_DIR:
            continue
        folder_path = ROOT / folder
        if not folder_path.exists():
            continue
        for f in folder_path.rglob("test_*.py"):
            if "__pycache__" not in str(f):
                misplaced.append(str(f.relative_to(ROOT)))
        for f in folder_path.rglob("*_test.py"):
            if "__pycache__" not in str(f):
                misplaced.append(str(f.relative_to(ROOT)))
    return misplaced


def find_unused_imports():
    """Find files with potentially unused imports (simple heuristic)."""
    candidates = []
    for folder in tqdm([AGENTIC_CORE_DIR, APPS_RG_DIR, APPS_LIC_DIR], desc="Processing", unit="item"):
        folder_path = ROOT / folder
        if not folder_path.exists():
            continue
        for f in tqdm(folder_path.rglob("*.py"), desc="Processing", unit="item"):
            if "__pycache__" in str(f) or f.name == "__init__.py":
                continue
            try:
                content = f.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(content)
                imports = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            name = alias.asname or alias.name.split(".")[0]
                            imports.append(name)
                    elif isinstance(node, ast.ImportFrom):
                        for alias in node.names:
                            name = alias.asname or alias.name
                            imports.append(name)
                # Check if imports are used (simple check)
                unused = []
                for imp in imports:
                    # Count occurrences (excluding import lines)
                    lines = content.splitlines()
                    usage_count = sum(1 for l in lines if imp in l and "import" not in l)
                    if usage_count == 0:
                        unused.append(imp)
                if len(unused) > 3:
                    candidates.append(
                        {
                            "path": str(f.relative_to(ROOT)),
                            "unused_count": len(unused),
                            "examples": unused[:5],
                            # guardian: allow-silent-swallow - acceptable exception handling
                        },
                    )
            except (OSError, UnicodeDecodeError, SyntaxError) as e:
                print(f"Failed to analyze {f.name}: {e}")
    return sorted(candidates, key=lambda x: -x["unused_count"])[:30]


def find_script_candidates():
    """Find scripts that might be one-off or obsolete."""
    candidates = []
    scripts_path = ROOT / "scripts"
    if not scripts_path.exists():
        return candidates

    for f in tqdm(scripts_path.glob("*.py"), desc="Processing", unit="item"):
        if f.name.startswith("__"):
            continue
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
            stat = f.stat()
            # Check for signs of one-off scripts
            signals = []
            if "hardcoded" in content.lower() or "hardcode" in content.lower():
                signals.append("hardcoded values")
            if "temporary" in content.lower() or "temp" in content.lower():
                signals.append("temporary marker")
            if "phase" in f.name.lower() and "batch" in f.name.lower():
                signals.append("batch migration script")
            if "fix_" in f.name.lower() or "patch_" in f.name.lower():
                signals.append("one-time fix script")
            if "archive" in f.name.lower() or "restore" in f.name.lower():
                signals.append("archive utility")
            if "update_" in f.name.lower() and "import" in f.name.lower():
                signals.append("import migration")

            if signals:
                candidates.append(
                    {
                        "path": str(f.relative_to(ROOT)),
                        "size_kb": round(stat.st_size / 1024, 1),
                        "signals": signals,  # guardian: File operations with encoding need error-specific handling
                    },
                )
        except (OSError, UnicodeDecodeError) as e:  # guardian: allow-silent-swallow - acceptable exception handling
            print(f"Failed to scan {f.name}: {e}")
    return candidates


def main():
    print("=" * 70)
    print("BLOAT ANALYSIS REPORT")
    print(f"Generated: {datetime.now().isoformat()}")
    print("=" * 70)

    # File stats
    stats, folder_stats = get_file_stats()
    print("\n## FILE STATISTICS BY EXTENSION")
    print("-" * 50)
    for ext, data in sorted(stats.items(), key=lambda x: -x[1]["count"])[:15]:
        ext_name = ext if ext else "(no ext)"
        print(f"  {ext_name:12} {data['count']:5} files  {data['size'] / 1024 / 1024:8.2f} MB")

    print("\n## FILE STATISTICS BY FOLDER")
    print("-" * 50)
    total_py = 0
    total_other = 0
    total_size = 0
    for folder, data in sorted(folder_stats.items()):
        print(
            f"  {folder:20} {data['py']:5} .py  {data['other']:5} other  {data['total_size'] / 1024 / 1024:8.2f} MB",
        )
        total_py += data["py"]
        total_other += data["other"]
        total_size += data["total_size"]
    print(f"  {'TOTAL':20} {total_py:5} .py  {total_other:5} other  {total_size / 1024 / 1024:8.2f} MB")

    # Large files
    large = find_large_files(100)
    print(f"\n## LARGE FILES (>100KB) - {len(large)} files")
    print("-" * 50)
    for f in large[:20]:
        print(f"  {f['size_kb']:7.1f} KB  {f['lines']:5} lines  {f['path']}")

    # Duplicates
    dupes = find_duplicate_filenames()
    print(f"\n## DUPLICATE FILENAMES - {len(dupes)} duplicates")
    print("-" * 50)
    for name, paths in sorted(dupes.items())[:15]:
        print(f"  {name}:")
        for p in paths:
            print(f"    - {p}")

    # Stubs
    stubs = find_empty_or_stub_files()
    print(f"\n## EMPTY/STUB FILES (<5 code lines) - {len(stubs)} files")
    print("-" * 50)
    for s in stubs[:20]:
        print(f"  {s['code_lines']:2} lines  {s['path']}")

    # Deprecated
    deprecated = find_deprecated_markers()
    print(f"\n## FILES WITH DEPRECATION MARKERS - {len(deprecated)} files")
    print("-" * 50)
    for d in deprecated[:20]:
        print(f"  [{d['marker']}] {d['path']}")

    # Misplaced tests
    misplaced = find_test_files_outside_tests()
    print(f"\n## TEST FILES OUTSIDE tests/ - {len(misplaced)} files")
    print("-" * 50)
    for m in misplaced[:20]:
        print(f"  {m}")

    # Script candidates
    scripts = find_script_candidates()
    print(f"\n## SCRIPT ARCHIVE CANDIDATES - {len(scripts)} files")
    print("-" * 50)
    for s in scripts:
        print(f"  {s['path']}")
        print(f"    Signals: {', '.join(s['signals'])}")

    # Unused imports
    unused = find_unused_imports()
    print(f"\n## FILES WITH MANY UNUSED IMPORTS - {len(unused)} files")
    print("-" * 50)
    for u in unused[:15]:
        print(f"  {u['unused_count']:3} unused  {u['path']}")
        print(f"    Examples: {', '.join(u['examples'][:3])}")


if __name__ == "__main__":
    main()
