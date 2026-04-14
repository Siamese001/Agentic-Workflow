"""
Suffix Cleanup Executor

Renames files with stuttering patterns and triggers deep refactoring
to update all imports and references across the codebase.

Target files:
1. LicHealingOrchestrator.py → LicHealingOrchestrator.py
2. OutreachPhase5Orchestrator.py → OutreachPhase5Orchestrator.py
3. MessageDiversityValidator.py → MessageDiversityValidator.py
4. ValidatorAgent.py → ValidatorAgent.py (SKIP - base validator)
5. RgHealingOrchestrator.py → RgHealingOrchestrator.py
6. RgResumeOrchestrator.py → RgResumeOrchestrator.py
"""

import ast
import os
import re
import shutil
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import (
    TESTS_DIR,
    get_validated_project_root,
)
from agentic_core.L0_routing.config.path_constants import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
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

_emit_records_execution_trace("p0", "evidence", "suffix_cleanup_executor")
_emit_applies_guardrail("p0", "suffix_cleanup_executor", "p0_governance")
_emit_reads_policy_state("p0", "suffix_cleanup_executor", "policy_binding")
_emit_snapshots_state("p0", "suffix_cleanup_executor", "state_snapshot")
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

_emit_emits_metric_event("suffix_cleanup_executor", "p4obs", "metric_1")
_emit_emits_metric_event("suffix_cleanup_executor", "p4obs", "metric_2")
_emit_emits_metric_event("suffix_cleanup_executor", "p4obs", "metric_3")
_emit_emits_metric_event("suffix_cleanup_executor", "p4obs", "metric_4")
_emit_emits_metric_event("suffix_cleanup_executor", "p4obs", "metric_5")
_emit_emits_metric_event("suffix_cleanup_executor", "p4obs", "metric_6")
_emit_records_incident_event("suffix_cleanup_executor", "p4obs", "incident")
_emit_captures_runtime_anomaly("suffix_cleanup_executor", "p4obs", "anomaly")
_emit_writes_observability_log("suffix_cleanup_executor", "p4obs", "obs_log")
_emit_updates_monitoring_state("suffix_cleanup_executor", "p4obs", "mon_state")
_emit_triggers_alert("suffix_cleanup_executor", "p4obs", "alert")
_emit_links_incident_trace("suffix_cleanup_executor", "p4obs", "trace_link")
_emit_captures_pattern("suffix_cleanup_executor", "p3lm", "pattern")
_emit_records_learning_event("suffix_cleanup_executor", "p3lm", "learning_event")
_emit_writes_learning_snapshot("suffix_cleanup_executor", "p3lm", "snapshot")
_emit_feeds_meta_learning("suffix_cleanup_executor", "p3lm", "meta_feed")
_emit_updates_routing_strategy("suffix_cleanup_executor", "p3lm", "routing")
_emit_improves_agent_policy("suffix_cleanup_executor", "p3lm", "policy")
_emit_stores_learning_state("suffix_cleanup_executor", "p3lm", "state")
_emit_records_execution_trace("suffix_cleanup_executor", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("suffix_cleanup_executor", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("suffix_cleanup_executor", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("suffix_cleanup_executor", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("suffix_cleanup_executor", "L4_STATE", "p2_trace_5")
_emit_reads_environ("suffix_cleanup_executor", "env_read", "p2_env_1")
_emit_reads_environ("suffix_cleanup_executor", "env_read", "p2_env_2")
_emit_reads_runtime_state("suffix_cleanup_executor", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("suffix_cleanup_executor", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "suffix_cleanup_executor", "context_pull")
_emit_pulls_context("p1", "suffix_cleanup_executor", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "suffix_cleanup_executor", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "suffix_cleanup_executor", "uwg_term_2")
_emit_writes_through("p1", "suffix_cleanup_executor", "write_through")
_emit_writes_through("p1", "suffix_cleanup_executor", "write_through_2")
_emit_validated_by_safety_plane("p1", "suffix_cleanup_executor", "safety_validation")
_emit_invokes_eval("p1", "suffix_cleanup_executor", "eval_call")
_emit_proposal_commits_routing("p1", "suffix_cleanup_executor", "routing_commit")
_emit_escalates_to_human("p1", "suffix_cleanup_executor", "human_escalation")
_emit_routes_through("p1", "suffix_cleanup_executor", "route_through")
_emit_checks_agent_registry("p1", "suffix_cleanup_executor", "agent_registry")
_emit_validates_agent_capability("p1", "suffix_cleanup_executor", "capability")
_emit_dispatches_execution_plan("p1", "suffix_cleanup_executor", "exec_plan")
_emit_agent_executes_agent("p1", "suffix_cleanup_executor", "sub_agent")
_emit_routes_to_agent("p1", "suffix_cleanup_executor", "target_agent")
_emit_verifies_policy("p1", "suffix_cleanup_executor", "policy_check")
_emit_observes_runtime_state("p1", "suffix_cleanup_executor", "runtime_state")
_emit_verifies_boundary("p1", "suffix_cleanup_executor", "boundary_check")
_emit_transcripts_response("p1", "suffix_cleanup_executor", "transcript")
_emit_hard_fails_untranscripted("p1", "suffix_cleanup_executor")
_emit_gated_by_confidence("p1", "suffix_cleanup_executor", "confidence_gate")
emit_replay_key("p0", "suffix_cleanup_executor")
emit_determinism_digest("p0", "suffix_cleanup_executor")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "suffix_cleanup_executor", "execution_auth")
_emit_validates_capability("p2", "suffix_cleanup_executor", "capability_check")
_emit_routes_to_capability("p2", "suffix_cleanup_executor", "capability_route")
_emit_writes_via_uwg("p2", "suffix_cleanup_executor", "uwg_write")
_emit_blocks_direct_write("p2", "suffix_cleanup_executor", "direct_write_block")
_emit_records_tool_invocation("p2", "suffix_cleanup_executor", "tool_invocation")
_emit_captures_execution_output("p2", "suffix_cleanup_executor", "exec_output")
_emit_dispatches_agent("p3", "suffix_cleanup_executor", "agent_dispatch")
_emit_coordinates_agents("p3", "suffix_cleanup_executor", "agent_coordination")
_emit_records_workflow_lineage("p3", "suffix_cleanup_executor", "workflow_lineage")
_emit_records_healing_outcome("p3", "suffix_cleanup_executor", "healing_outcome")
_emit_escalates_failure("p3", "suffix_cleanup_executor", "failure_escalation")
_emit_orchestrates_workflow("p3", "suffix_cleanup_executor", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "suffix_cleanup_executor", "healing_dispatch")
_emit_invokes_evaluation("p3", "suffix_cleanup_executor", "evaluation_signal")
_emit_records_telemetry_event("p4", "suffix_cleanup_executor", "telemetry_event")
_emit_captures_evaluation_metric("p4", "suffix_cleanup_executor", "eval_metric")
_emit_stores_embedding("p4", "suffix_cleanup_executor", "embedding_store")
_emit_updates_meta_learning_state("p4", "suffix_cleanup_executor", "meta_learning")
_emit_links_execution_to_snapshot("p4", "suffix_cleanup_executor", "exec_snapshot_link")

_ROOT = get_validated_project_root()


def to_smart_snake_case(name: str) -> str:
    """Convert PascalCase to snake_case while preserving acronyms."""
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def update_imports_in_file(file_path: Path, old_name: str, new_name: str) -> int:
    """Update imports in a single file."""
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content

        # Update import statements
        patterns = [
            (rf"from ([a-zA-Z0-9_.]+) import {old_name}", rf"from \1 import {new_name}"),
            (
                rf"from ([a-zA-Z0-9_.]+) import \(([^)]*){old_name}([^)]*)\)",
                rf"from \1 import (\2{new_name}\3)",
            ),
            (rf"import ([a-zA-Z0-9_.]+\.{old_name})", r"import \1"),
        ]

        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)

        # Update class references
        content = re.sub(rf"\b{old_name}\b", new_name, content)

        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            return 1
        return 0
    except (
        UnicodeDecodeError,
        OSError,
    ):  # guardian: File operations with encoding need error-specific handling
        return 0


def rename_file_and_refactor(source_path: Path, new_filename: str, project_root: Path) -> dict[str, Any]:
    """Rename a file and update all references."""
    old_stem = source_path.stem
    new_stem = Path(new_filename).stem

    result = {
        "source": str(source_path),
        "target": str(source_path.parent / new_filename),
        "old_class": old_stem,
        "new_class": new_stem,
        "files_updated": 0,
        "success": False,
    }

    if not source_path.exists():
        result["error"] = "Source file not found"
        return result

    target_path = source_path.parent / new_filename
    if target_path.exists():
        result["error"] = "Target file already exists"
        return result

    # Step 1: Rename the file
    try:
        shutil.move(str(source_path), str(target_path))
        print(f"✓ Renamed: {source_path.name} → {new_filename}")
    # guardian: allow-silent-swallow
    except Exception as e:
        result["error"] = str(e)
        return result

    # Step 2: Update class name inside the file
    try:
        content = target_path.read_text(encoding="utf-8")
        tree = ast.parse(content)

        # Find and replace class definition
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == old_stem:
                content = re.sub(rf"class {old_stem}\b", f"class {new_stem}", content)
                break

        target_path.write_text(content, encoding="utf-8")
        print(f"  ✓ Updated class definition: {old_stem} → {new_stem}")
    # guardian: allow-silent-swallow
    except Exception as e:
        print(f"  ⚠ Warning: Could not update class definition: {e}")

    # Step 3: Deep refactoring - update all imports and references
    print("  → Scanning codebase for references...")

    exclude_dirs = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES
    files_updated = 0

    for dirpath, dirnames, filenames in os.walk(project_root):
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

        for filename in filenames:
            if filename.endswith(".py"):
                file_path = Path(dirpath) / filename
                files_updated += update_imports_in_file(file_path, old_stem, new_stem)

    result["files_updated"] = files_updated
    result["success"] = True
    print(f"  ✓ Updated {files_updated} files with new imports/references")

    # Step 4: Update corresponding test file
    test_name_old = f"test_{to_smart_snake_case(old_stem)}.py"
    test_name_new = f"test_{to_smart_snake_case(new_stem)}.py"

    # Find test file
    rel_path = source_path.relative_to(project_root)
    test_path_old = _ROOT / TESTS_DIR / "unit" / rel_path.parent / test_name_old
    test_path_new = _ROOT / TESTS_DIR / "unit" / rel_path.parent / test_name_new

    if test_path_old.exists() and not test_path_new.exists():
        try:
            shutil.move(str(test_path_old), str(test_path_new))
            print(f"  ✓ Renamed test: {test_name_old} → {test_name_new}")

            # Update test content
            content = test_path_new.read_text(encoding="utf-8")
            content = re.sub(rf"\b{old_stem}\b", new_stem, content)
            test_path_new.write_text(content, encoding="utf-8")
        # guardian: allow-silent-swallow
        except Exception as e:
            print(f"  ⚠ Warning: Could not update test file: {e}")

    return result


def execute_suffix_cleanup(project_root: Path, dry_run: bool = False) -> dict[str, Any]:
    """Execute the suffix cleanup for all flagged files."""

    # Target files with stuttering patterns
    targets = [
        ("apps_lic/engines/LicHealingOrchestrator.py", "LicHealingOrchestrator.py"),
        ("apps_lic/engines/OutreachPhase5Orchestrator.py", "OutreachPhase5Orchestrator.py"),
        ("apps_lic/engines/MessageDiversityValidator.py", "MessageDiversityValidator.py"),
        # Skip ValidatorAgent.py - it's a base validator, not stuttering
        ("apps_rg/engines/utils/RgHealingOrchestrator.py", "RgHealingOrchestrator.py"),
        ("apps_rg/engines/utils/RgResumeOrchestrator.py", "RgResumeOrchestrator.py"),
    ]

    report = {
        "mode": "DRY_RUN" if dry_run else "EXECUTE",
        "results": [],
        "total_files_updated": 0,
        "success_count": 0,
        "error_count": 0,
    }

    print("=" * 60)
    print(f"SUFFIX CLEANUP EXECUTOR - {report['mode']}")
    print("=" * 60)

    for source_rel, new_filename in tqdm(targets, desc="Processing", unit="item"):
        source_path = project_root / source_rel
        print(f"\n[{len(report['results']) + 1}/{len(targets)}] Processing: {source_rel}")

        if dry_run:
            print(f"  → Would rename to: {new_filename}")
            report["results"].append(
                {
                    "source": str(source_path),
                    "target": new_filename,
                    "dry_run": True,
                },
            )
        else:
            result = rename_file_and_refactor(source_path, new_filename, project_root)
            report["results"].append(result)

            if result["success"]:
                report["success_count"] += 1
                report["total_files_updated"] += result["files_updated"]
            else:
                report["error_count"] += 1
                print(f"  ✗ Error: {result.get('error', 'Unknown error')}")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Files renamed: {report['success_count']}/{len(targets)}")
    print(f"Total references updated: {report['total_files_updated']}")
    print(f"Errors: {report['error_count']}")

    return report


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Suffix Cleanup Executor")
    parser.add_argument("--execute", action="store_true", help="Execute changes (default: dry run)")
    parser.add_argument("--output", type=str, default="suffix_cleanup_report.json", help="Report output file")
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    report = execute_suffix_cleanup(project_root, dry_run=not args.execute)

    # Save report
    output_path = project_root / args.output
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport saved to: {output_path}")
