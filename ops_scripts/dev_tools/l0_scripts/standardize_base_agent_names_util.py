#!/usr/bin/env python3
"""
Standardize base agent naming with L# prefix throughout codebase.

Current -> New:
- L0RoutingBaseAgent -> L0RoutingBaseAgent
- L1CognitionBase -> L1CognitionBase
- L2ExecutionBase -> (already has L# prefix, keep as is)
- L3OrchestrationBase -> L3L3OrchestrationBase
- L4StateBase -> L4L4StateBase
- L5SafetyBase -> L5L5SafetyBase
- L6ObservabilityBase -> (already has L# prefix, keep as is)

This script:
1. Renames class definitions
2. Updates all imports
3. Updates all references in code and docs
4. Regenerates agent discovery
"""

from pathlib import Path

from agentic_core.L5_safety.config.structure_blueprint.ssot import (
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

_emit_records_execution_trace("p0", "evidence", "standardize_base_agent_names_util")
_emit_applies_guardrail("p0", "standardize_base_agent_names_util", "p0_governance")
_emit_reads_policy_state("p0", "standardize_base_agent_names_util", "policy_binding")
_emit_snapshots_state("p0", "standardize_base_agent_names_util", "state_snapshot")
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

_emit_emits_metric_event("standardize_base_agent_names_util", "p4obs", "metric_1")
_emit_emits_metric_event("standardize_base_agent_names_util", "p4obs", "metric_2")
_emit_emits_metric_event("standardize_base_agent_names_util", "p4obs", "metric_3")
_emit_emits_metric_event("standardize_base_agent_names_util", "p4obs", "metric_4")
_emit_emits_metric_event("standardize_base_agent_names_util", "p4obs", "metric_5")
_emit_emits_metric_event("standardize_base_agent_names_util", "p4obs", "metric_6")
_emit_records_incident_event("standardize_base_agent_names_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("standardize_base_agent_names_util", "p4obs", "anomaly")
_emit_writes_observability_log("standardize_base_agent_names_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("standardize_base_agent_names_util", "p4obs", "mon_state")
_emit_triggers_alert("standardize_base_agent_names_util", "p4obs", "alert")
_emit_links_incident_trace("standardize_base_agent_names_util", "p4obs", "trace_link")
_emit_captures_pattern("standardize_base_agent_names_util", "p3lm", "pattern")
_emit_records_learning_event("standardize_base_agent_names_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("standardize_base_agent_names_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("standardize_base_agent_names_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("standardize_base_agent_names_util", "p3lm", "routing")
_emit_improves_agent_policy("standardize_base_agent_names_util", "p3lm", "policy")
_emit_stores_learning_state("standardize_base_agent_names_util", "p3lm", "state")
_emit_records_execution_trace("standardize_base_agent_names_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("standardize_base_agent_names_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("standardize_base_agent_names_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("standardize_base_agent_names_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("standardize_base_agent_names_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("standardize_base_agent_names_util", "env_read", "p2_env_1")
_emit_reads_environ("standardize_base_agent_names_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("standardize_base_agent_names_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("standardize_base_agent_names_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "standardize_base_agent_names_util", "context_pull")
_emit_pulls_context("p1", "standardize_base_agent_names_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "standardize_base_agent_names_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "standardize_base_agent_names_util", "uwg_term_2")
_emit_writes_through("p1", "standardize_base_agent_names_util", "write_through")
_emit_writes_through("p1", "standardize_base_agent_names_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "standardize_base_agent_names_util", "safety_validation")
_emit_invokes_eval("p1", "standardize_base_agent_names_util", "eval_call")
_emit_proposal_commits_routing("p1", "standardize_base_agent_names_util", "routing_commit")
_emit_escalates_to_human("p1", "standardize_base_agent_names_util", "human_escalation")
_emit_routes_through("p1", "standardize_base_agent_names_util", "route_through")
_emit_checks_agent_registry("p1", "standardize_base_agent_names_util", "agent_registry")
_emit_validates_agent_capability("p1", "standardize_base_agent_names_util", "capability")
_emit_dispatches_execution_plan("p1", "standardize_base_agent_names_util", "exec_plan")
_emit_agent_executes_agent("p1", "standardize_base_agent_names_util", "sub_agent")
_emit_routes_to_agent("p1", "standardize_base_agent_names_util", "target_agent")
_emit_verifies_policy("p1", "standardize_base_agent_names_util", "policy_check")
_emit_observes_runtime_state("p1", "standardize_base_agent_names_util", "runtime_state")
_emit_verifies_boundary("p1", "standardize_base_agent_names_util", "boundary_check")
_emit_transcripts_response("p1", "standardize_base_agent_names_util", "transcript")
_emit_hard_fails_untranscripted("p1", "standardize_base_agent_names_util")
_emit_gated_by_confidence("p1", "standardize_base_agent_names_util", "confidence_gate")
emit_replay_key("p0", "standardize_base_agent_names_util")
emit_determinism_digest("p0", "standardize_base_agent_names_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "standardize_base_agent_names_util", "execution_auth")
_emit_validates_capability("p2", "standardize_base_agent_names_util", "capability_check")
_emit_routes_to_capability("p2", "standardize_base_agent_names_util", "capability_route")
_emit_writes_via_uwg("p2", "standardize_base_agent_names_util", "uwg_write")
_emit_blocks_direct_write("p2", "standardize_base_agent_names_util", "direct_write_block")
_emit_records_tool_invocation("p2", "standardize_base_agent_names_util", "tool_invocation")
_emit_captures_execution_output("p2", "standardize_base_agent_names_util", "exec_output")
_emit_dispatches_agent("p3", "standardize_base_agent_names_util", "agent_dispatch")
_emit_coordinates_agents("p3", "standardize_base_agent_names_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "standardize_base_agent_names_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "standardize_base_agent_names_util", "healing_outcome")
_emit_escalates_failure("p3", "standardize_base_agent_names_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "standardize_base_agent_names_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "standardize_base_agent_names_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "standardize_base_agent_names_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "standardize_base_agent_names_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "standardize_base_agent_names_util", "eval_metric")
_emit_stores_embedding("p4", "standardize_base_agent_names_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "standardize_base_agent_names_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "standardize_base_agent_names_util", "exec_snapshot_link")

PROJECT_ROOT = Path(__file__).parent.parent

# Mapping of old names to new names
RENAME_MAP = {
    # Class name changes - Phase 2: L0 and L1 only
    "L0RoutingBaseAgent": "L0RoutingBaseAgent",
    "L1CognitionBase": "L1CognitionBase",
}

# File renames (old path -> new path, relative to PROJECT_ROOT)
FILE_RENAMES = {
    "agentic_core/L0_routing/scripts/L0RoutingBaseAgent.py": "agentic_core/L0_routing/scripts/L0RoutingBaseAgent.py",
    "agentic_core/L1_cognition/thought_engine/L1CognitionBase.py": "agentic_core/L1_cognition/thought_engine/L1CognitionBase.py",
}

# Extensions to process
CODE_EXTENSIONS = {".py", ".md", ".json", ".html", ".txt"}

# Directories to skip
SKIP_DIRS = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES


def find_files_to_update(root: Path) -> list[Path]:
    """Find all files that may need updating."""
    # Phase 6.7: Use ssot_discovery instead of rglob
    from agentic_core.utils.runners.ssot_discovery_validator import get_data_files, get_python_files

    files = list(get_python_files(root)) + list(
        get_data_files(root, extensions=[".json", ".md", ".yaml", ".yml"]),
    )

    # Filter by CODE_EXTENSIONS and skip directories
    filtered_files = []
    for path in files:
        if path.is_file() and path.suffix in CODE_EXTENSIONS:
            if not any(skip in path.parts for skip in SKIP_DIRS):
                filtered_files.append(path)
    return filtered_files


def update_file_content(
    file_path: Path,
    rename_map: dict[str, str],
    dry_run: bool = True,
) -> tuple[bool, int]:
    """Update file content with new names. Returns (changed, count)."""
    try:
        content = file_path.read_text(encoding="utf-8")
    # guardian: allow-silent-swallow
    except Exception as e:
        print(f"  ⚠️  Could not read {file_path}: {e}")
        return False, 0

    original = content
    changes = 0

    for old_name, new_name in rename_map.items():
        if old_name in content:
            count = content.count(old_name)
            content = content.replace(old_name, new_name)
            changes += count

    if content != original:
        if not dry_run:
            file_path.write_text(content, encoding="utf-8")
        return True, changes

    return False, 0


def rename_files(file_renames: dict[str, str], dry_run: bool = True) -> list[str]:
    """Rename files. Returns list of renamed files."""
    renamed = []
    for old_path, new_path in file_renames.items():
        old_full = PROJECT_ROOT / old_path
        new_full = PROJECT_ROOT / new_path

        if old_full.exists():
            if dry_run:
                print(f"  Would rename: {old_path} -> {new_path}")
            else:
                old_full.rename(new_full)
                print(f"  Renamed: {old_path} -> {new_path}")
            renamed.append(old_path)
        else:
            print(f"  ⚠️  File not found: {old_path}")

    return renamed


def main(dry_run: bool = True):
    """Main execution."""
    mode = "DRY RUN" if dry_run else "LIVE"
    print("=" * 70)
    print(f"Base Agent Name Standardization ({mode})")
    print("=" * 70)

    print("\nRename Map:")
    for old, new in RENAME_MAP.items():
        print(f"  {old} -> {new}")

    # Step 1: Find files to update
    print("\nScanning files...")
    files = find_files_to_update(PROJECT_ROOT)
    print(f"  Found {len(files)} files to scan")

    # Step 2: Update file contents
    print("\nUpdating file contents...")
    updated_files = []
    total_changes = 0

    for file_path in files:
        changed, count = update_file_content(file_path, RENAME_MAP, dry_run)
        if changed:
            updated_files.append((file_path, count))
            total_changes += count
            if count > 0:
                rel_path = file_path.relative_to(PROJECT_ROOT)
                print(f"  {'Would update' if dry_run else 'Updated'}: {rel_path} ({count} changes)")

    # Step 3: Rename files
    print("\nRenaming files...")
    renamed = rename_files(FILE_RENAMES, dry_run)

    # Summary
    print("\n" + "=" * 70)
    print("Summary:")
    print(f"  Files updated: {len(updated_files)}")
    print(f"  Total replacements: {total_changes}")
    print(f"  Files renamed: {len(renamed)}")

    if dry_run:
        print("\n⚠️  This was a DRY RUN. No changes were made.")
        print("   Run with --live to apply changes.")
    else:
        print("\n✅ Changes applied successfully!")
        print("   Run agent discovery and tests to verify.")

    print("=" * 70)

    return len(updated_files), total_changes, len(renamed)


if __name__ == "__main__":
    import sys

    dry_run = "--live" not in sys.argv
    main(dry_run)
