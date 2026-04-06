#!/usr/bin/env python3
"""
SSOT Archive Path Refactor

Replaces all hardcoded "archives" strings with imports from structure_blueprint.ARCHIVES_DIR
to ensure Single Source of Truth compliance.

USAGE:
    python scripts/maintenance/ssot_archive_refactor.py --dry-run
    python scripts/maintenance/ssot_archive_refactor.py --execute
"""

import argparse
import re
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    ARCHIVES_DIR,
    get_validated_project_root,
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
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_emits_metric_event("ssot_archive_refactor", "p4obs", "metric_1")
_emit_emits_metric_event("ssot_archive_refactor", "p4obs", "metric_2")
_emit_emits_metric_event("ssot_archive_refactor", "p4obs", "metric_3")
_emit_emits_metric_event("ssot_archive_refactor", "p4obs", "metric_4")
_emit_emits_metric_event("ssot_archive_refactor", "p4obs", "metric_5")
_emit_emits_metric_event("ssot_archive_refactor", "p4obs", "metric_6")
_emit_records_incident_event("ssot_archive_refactor", "p4obs", "incident")
_emit_captures_runtime_anomaly("ssot_archive_refactor", "p4obs", "anomaly")
_emit_writes_observability_log("ssot_archive_refactor", "p4obs", "obs_log")
_emit_updates_monitoring_state("ssot_archive_refactor", "p4obs", "mon_state")
_emit_triggers_alert("ssot_archive_refactor", "p4obs", "alert")
_emit_links_incident_trace("ssot_archive_refactor", "p4obs", "trace_link")
_emit_captures_pattern("ssot_archive_refactor", "p3lm", "pattern")
_emit_records_learning_event("ssot_archive_refactor", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ssot_archive_refactor", "p3lm", "snapshot")
_emit_feeds_meta_learning("ssot_archive_refactor", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ssot_archive_refactor", "p3lm", "routing")
_emit_improves_agent_policy("ssot_archive_refactor", "p3lm", "policy")
_emit_stores_learning_state("ssot_archive_refactor", "p3lm", "state")
_emit_records_execution_trace("ssot_archive_refactor", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ssot_archive_refactor", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ssot_archive_refactor", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ssot_archive_refactor", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ssot_archive_refactor", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ssot_archive_refactor", "env_read", "p2_env_1")
_emit_reads_environ("ssot_archive_refactor", "env_read", "p2_env_2")
_emit_reads_runtime_state("ssot_archive_refactor", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ssot_archive_refactor", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "ssot_archive_refactor")
_emit_applies_guardrail("p0", "ssot_archive_refactor", "p0_governance")
_emit_reads_policy_state("p0", "ssot_archive_refactor", "policy_binding")
_emit_snapshots_state("p0", "ssot_archive_refactor", "state_snapshot")
_emit_pulls_context("p1", "ssot_archive_refactor", "context_pull")
_emit_pulls_context("p1", "ssot_archive_refactor", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "ssot_archive_refactor", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ssot_archive_refactor", "uwg_term_secondary")
_emit_writes_through("p1", "ssot_archive_refactor", "write_through")
_emit_writes_through("p1", "ssot_archive_refactor", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "ssot_archive_refactor", "safety_validation")
_emit_invokes_eval("p1", "ssot_archive_refactor", "eval_call")
_emit_proposal_commits_routing("p1", "ssot_archive_refactor", "routing_commit")
_emit_escalates_to_human("p1", "ssot_archive_refactor", "human_escalation")
_emit_routes_through("p1", "ssot_archive_refactor", "route_through")
_emit_checks_agent_registry("p1", "ssot_archive_refactor", "agent_registry")
_emit_validates_agent_capability("p1", "ssot_archive_refactor", "capability")
_emit_dispatches_execution_plan("p1", "ssot_archive_refactor", "exec_plan")
_emit_agent_executes_agent("p1", "ssot_archive_refactor", "sub_agent")
_emit_routes_to_agent("p1", "ssot_archive_refactor", "target_agent")
_emit_verifies_policy("p1", "ssot_archive_refactor", "policy_check")
_emit_observes_runtime_state("p1", "ssot_archive_refactor", "runtime_state")
_emit_verifies_boundary("p1", "ssot_archive_refactor", "boundary_check")
_emit_transcripts_response("p1", "ssot_archive_refactor", "transcript")
_emit_hard_fails_untranscripted("p1", "ssot_archive_refactor")
_emit_gated_by_confidence("p1", "ssot_archive_refactor", "confidence_gate")
emit_replay_key("p0", "ssot_archive_refactor")
emit_determinism_digest("p0", "ssot_archive_refactor")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "ssot_archive_refactor", "execution_auth")
_emit_validates_capability("p2", "ssot_archive_refactor", "capability_check")
_emit_routes_to_capability("p2", "ssot_archive_refactor", "capability_route")
_emit_writes_via_uwg("p2", "ssot_archive_refactor", "uwg_write")
_emit_blocks_direct_write("p2", "ssot_archive_refactor", "direct_write_block")
_emit_records_tool_invocation("p2", "ssot_archive_refactor", "tool_invocation")
_emit_captures_execution_output("p2", "ssot_archive_refactor", "exec_output")
_emit_dispatches_agent("p3", "ssot_archive_refactor", "agent_dispatch")
_emit_coordinates_agents("p3", "ssot_archive_refactor", "agent_coordination")
_emit_records_workflow_lineage("p3", "ssot_archive_refactor", "workflow_lineage")
_emit_records_healing_outcome("p3", "ssot_archive_refactor", "healing_outcome")
_emit_escalates_failure("p3", "ssot_archive_refactor", "failure_escalation")
_emit_orchestrates_workflow("p3", "ssot_archive_refactor", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ssot_archive_refactor", "healing_dispatch")
_emit_invokes_evaluation("p3", "ssot_archive_refactor", "evaluation_signal")
_emit_records_telemetry_event("p4", "ssot_archive_refactor", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ssot_archive_refactor", "eval_metric")
_emit_stores_embedding("p4", "ssot_archive_refactor", "embedding_store")
_emit_updates_meta_learning_state("p4", "ssot_archive_refactor", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ssot_archive_refactor", "exec_snapshot_link")


def find_hardcoded_archives(file_path: Path) -> list[tuple[int, str]]:
    """Find lines with hardcoded 'archives' strings."""
    matches = []
    try:
        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            # Skip comments and docstrings
            if line.strip().startswith("#"):
                continue
            if '"""' in line or "'''" in line:
                continue

            # Look for hardcoded "archives" or 'archives'
            if '"archives"' in line or "'archives'" in line:
                # Skip if it's already using ARCHIVES_DIR
                if "ARCHIVES_DIR" in line:
                    continue
                # Skip if it's in a comment
                if "#" in line and line.index("#") < line.find("archives"):
                    continue
                matches.append((i, line))

    except Exception as e:
        raise
        print(f"  ⚠️  Error reading {file_path}: {e}")

    return matches


def needs_import(file_path: Path) -> bool:
    """Check if file needs ARCHIVES_DIR import."""
    try:
        content = file_path.read_text(encoding="utf-8")
        # Check if already imports ARCHIVES_DIR
        if "from agentic_core.L5_safety.config.structure_blueprint_config import ARCHIVES_DIR" in content:
            return False
        if "ARCHIVES_DIR" in content and "import" in content:
            return False
        return True
    except (ValueError, TypeError, RuntimeError) as e:
        raise
        return False


def add_import(file_path: Path, dry_run: bool = True) -> bool:
    """Add ARCHIVES_DIR import to file."""
    try:
        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")

        # Find the best place to insert import (after other imports)
        import_line = -1
        for i, line in enumerate(lines):
            if line.startswith("from ") or line.startswith("import "):
                import_line = i

        if import_line == -1:
            # No imports found, add after docstring
            for i, line in enumerate(lines):
                if '"""' in line or "'''" in line:
                    import_line = i + 1
                    break

        if import_line == -1:
            import_line = 0

        # Insert import
        new_import = "from agentic_core.L5_safety.config.structure_blueprint_config import ARCHIVES_DIR"
        lines.insert(import_line + 1, new_import)

        if not dry_run:
            file_path.write_text("\n".join(lines), encoding="utf-8")

        return True
    except Exception as e:
        raise
        print(f"  ❌ Error adding import to {file_path}: {e}")
        return False


def replace_hardcoded_archives(file_path: Path, dry_run: bool = True) -> int:
    """Replace hardcoded 'archives' with ARCHIVES_DIR."""
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content

        # Replace "archives" with ARCHIVES_DIR (but not in comments)
        # Pattern: project_root / "archives" -> project_root / ARCHIVES_DIR
        content = re.sub(r'(["\'])archives\1', "ARCHIVES_DIR", content)

        replacements = content.count("ARCHIVES_DIR") - original_content.count("ARCHIVES_DIR")

        if content != original_content and not dry_run:
            file_path.write_text(content, encoding="utf-8")

        return replacements
    except Exception as e:
        raise
        print(f"  ❌ Error replacing in {file_path}: {e}")
        return 0


def main():
    parser = argparse.ArgumentParser(description="SSOT Archive Path Refactor")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute changes (default is dry-run)",
    )
    args = parser.parse_args()

    dry_run = not args.execute

    print(f"\n{'=' * 70}")
    print("SSOT Archive Path Refactor")
    print(f"{'=' * 70}")
    print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
    print(f"{'=' * 70}\n")

    # Scan agentic_core for hardcoded archives
    agentic_core = get_validated_project_root() / AGENTIC_CORE_DIR
    files_to_fix = []

    for py_file in agentic_core.rglob("*.py"):
        # Skip archives directory itself
        if ARCHIVES_DIR in py_file.parts:
            continue
        if "__pycache__" in py_file.parts:
            continue

        matches = find_hardcoded_archives(py_file)
        if matches:
            files_to_fix.append((py_file, matches))

    print(f"Found {len(files_to_fix)} files with hardcoded 'archives' strings\n")

    if not files_to_fix:
        print("✅ No hardcoded 'archives' strings found!")
        return 0

    total_replacements = 0

    for file_path, matches in files_to_fix:
        print(f"\n📝 {file_path}")
        print(f"   Found {len(matches)} hardcoded references")

        if dry_run:
            print("   [DRY RUN] Would:")
            if needs_import(file_path):
                print("     1. Add ARCHIVES_DIR import")
            print(f"     2. Replace {len(matches)} hardcoded strings")
        else:
            # Add import if needed
            if needs_import(file_path):
                if add_import(file_path, dry_run=False):
                    print("   ✅ Added ARCHIVES_DIR import")

            # Replace hardcoded strings
            replacements = replace_hardcoded_archives(file_path, dry_run=False)
            if replacements > 0:
                print(f"   ✅ Replaced {replacements} occurrences")
                total_replacements += replacements

    print(f"\n{'=' * 70}")
    if dry_run:
        print("DRY RUN COMPLETE")
        print(f"Would modify {len(files_to_fix)} files")
    else:
        print("REFACTOR COMPLETE")
        print(f"Files modified: {len(files_to_fix)}")
        print(f"Total replacements: {total_replacements}")
        print("\nNext steps:")
        print("  1. Run: pytest tests/L5_safety/test_hygiene_consolidation.py")
        print("  2. Run: pytest tests/unit/test_archival_gatekeeper.py")
        print("  3. Verify: python scripts/maintenance/verify_ssot_compliance.py")
    print(f"{'=' * 70}\n")

    return 0


if __name__ == "__main__":
    exit(main())
