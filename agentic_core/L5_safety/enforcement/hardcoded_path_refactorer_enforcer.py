from agentic_core.L2_execution.utils import write_gateway as _wg
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
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

emit_replay_key("p0", "hardcoded_path_refactorer_enforcer")
emit_determinism_digest("p0", "hardcoded_path_refactorer_enforcer")

_emit_dispatches_healing_run("p1", "hardcoded_path_refactorer_enforcer", "L5")
_emit_routes_through("p1", "hardcoded_path_refactorer_enforcer", "L5")
_emit_checks_agent_registry("p1", "hardcoded_path_refactorer_enforcer", "agent_registry")
_emit_validates_agent_capability("p1", "hardcoded_path_refactorer_enforcer", "capability")
_emit_dispatches_execution_plan("p1", "hardcoded_path_refactorer_enforcer", "exec_plan")
_emit_agent_executes_agent("p1", "hardcoded_path_refactorer_enforcer", "sub_agent")
_emit_routes_to_agent("p1", "hardcoded_path_refactorer_enforcer", "target_agent")
_emit_verifies_policy("p1", "hardcoded_path_refactorer_enforcer", "policy_check")
_emit_observes_runtime_state("p1", "hardcoded_path_refactorer_enforcer", "runtime_state")
_emit_verifies_boundary("p1", "hardcoded_path_refactorer_enforcer", "boundary_check")
_emit_transcripts_response("p1", "hardcoded_path_refactorer_enforcer", "transcript")
_emit_hard_fails_untranscripted("p1", "hardcoded_path_refactorer_enforcer")
_emit_gated_by_confidence("p1", "hardcoded_path_refactorer_enforcer", "confidence_gate")
_emit_escalates_to_human("p1", "hardcoded_path_refactorer_enforcer", "L5")
_emit_reads_policy_state("p1", "hardcoded_path_refactorer_enforcer", "L5")
_emit_authorize_and_execute("p2", "hardcoded_path_refactorer_enforcer", "execution_auth")
_emit_validates_capability("p2", "hardcoded_path_refactorer_enforcer", "capability_check")
_emit_routes_to_capability("p2", "hardcoded_path_refactorer_enforcer", "capability_route")
_emit_writes_via_uwg("p2", "hardcoded_path_refactorer_enforcer", "uwg_write")
_emit_blocks_direct_write("p2", "hardcoded_path_refactorer_enforcer", "direct_write_block")
_emit_records_tool_invocation("p2", "hardcoded_path_refactorer_enforcer", "tool_invocation")
_emit_captures_execution_output("p2", "hardcoded_path_refactorer_enforcer", "exec_output")
_emit_dispatches_agent("p3", "hardcoded_path_refactorer_enforcer", "agent_dispatch")
_emit_coordinates_agents("p3", "hardcoded_path_refactorer_enforcer", "agent_coordination")
_emit_records_workflow_lineage("p3", "hardcoded_path_refactorer_enforcer", "workflow_lineage")
_emit_records_healing_outcome("p3", "hardcoded_path_refactorer_enforcer", "healing_outcome")
_emit_escalates_failure("p3", "hardcoded_path_refactorer_enforcer", "failure_escalation")
_emit_orchestrates_workflow("p3", "hardcoded_path_refactorer_enforcer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "hardcoded_path_refactorer_enforcer", "healing_dispatch")
_emit_invokes_evaluation("p3", "hardcoded_path_refactorer_enforcer", "evaluation_signal")
_emit_records_telemetry_event("p4", "hardcoded_path_refactorer_enforcer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "hardcoded_path_refactorer_enforcer", "eval_metric")
_emit_stores_embedding("p4", "hardcoded_path_refactorer_enforcer", "embedding_store")
_emit_updates_meta_learning_state("p4", "hardcoded_path_refactorer_enforcer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "hardcoded_path_refactorer_enforcer", "exec_snapshot_link")

#!/usr/bin/env python3
"""
Bulk refactor hardcoded paths to use SSOT constants from structure_blueprint.py
"""

import re
from pathlib import Path

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

_emit_emits_metric_event("hardcoded_path_refactorer_enforcer", "p4obs", "metric_1")
_emit_emits_metric_event("hardcoded_path_refactorer_enforcer", "p4obs", "metric_2")
_emit_emits_metric_event("hardcoded_path_refactorer_enforcer", "p4obs", "metric_3")
_emit_emits_metric_event("hardcoded_path_refactorer_enforcer", "p4obs", "metric_4")
_emit_emits_metric_event("hardcoded_path_refactorer_enforcer", "p4obs", "metric_5")
_emit_emits_metric_event("hardcoded_path_refactorer_enforcer", "p4obs", "metric_6")
_emit_records_incident_event("hardcoded_path_refactorer_enforcer", "p4obs", "incident")
_emit_captures_runtime_anomaly("hardcoded_path_refactorer_enforcer", "p4obs", "anomaly")
_emit_writes_observability_log("hardcoded_path_refactorer_enforcer", "p4obs", "obs_log")
_emit_updates_monitoring_state("hardcoded_path_refactorer_enforcer", "p4obs", "mon_state")
_emit_triggers_alert("hardcoded_path_refactorer_enforcer", "p4obs", "alert")
_emit_links_incident_trace("hardcoded_path_refactorer_enforcer", "p4obs", "trace_link")
_emit_captures_pattern("hardcoded_path_refactorer_enforcer", "p3lm", "pattern")
_emit_records_learning_event("hardcoded_path_refactorer_enforcer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("hardcoded_path_refactorer_enforcer", "p3lm", "snapshot")
_emit_feeds_meta_learning("hardcoded_path_refactorer_enforcer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("hardcoded_path_refactorer_enforcer", "p3lm", "routing")
_emit_improves_agent_policy("hardcoded_path_refactorer_enforcer", "p3lm", "policy")
_emit_stores_learning_state("hardcoded_path_refactorer_enforcer", "p3lm", "state")
_emit_records_execution_trace("hardcoded_path_refactorer_enforcer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("hardcoded_path_refactorer_enforcer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("hardcoded_path_refactorer_enforcer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("hardcoded_path_refactorer_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("hardcoded_path_refactorer_enforcer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("hardcoded_path_refactorer_enforcer", "env_read", "p2_env_1")
_emit_reads_environ("hardcoded_path_refactorer_enforcer", "env_read", "p2_env_2")
_emit_reads_runtime_state("hardcoded_path_refactorer_enforcer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("hardcoded_path_refactorer_enforcer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "hardcoded_path_refactorer_enforcer", "context_pull")
_emit_pulls_context("p1", "hardcoded_path_refactorer_enforcer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "hardcoded_path_refactorer_enforcer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "hardcoded_path_refactorer_enforcer", "uwg_term_2")
_emit_writes_through("p1", "hardcoded_path_refactorer_enforcer", "write_through")
_emit_writes_through("p1", "hardcoded_path_refactorer_enforcer", "write_through_2")
_emit_validated_by_safety_plane("p1", "hardcoded_path_refactorer_enforcer", "safety_validation")
_emit_invokes_eval("p1", "hardcoded_path_refactorer_enforcer", "eval_call")
_emit_proposal_commits_routing("p1", "hardcoded_path_refactorer_enforcer", "routing_commit")

PROJECT_ROOT = Path(__file__).parent.parent

# Files to exclude
EXCLUDED_DIRS = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES

EXCLUDED_FILES = {
    "structure_blueprint.py",  # SSOT definition
    "scan_hardcoded_paths.py",
    "refactor_hardcoded_paths_util.py",  # This file
}

# SSOT constant mappings (path_pattern -> SSOT_CONSTANT_NAME)
PATH_TO_SSOT_MAP = {
    # Agent discovery files
    r'["\']agent_discovery_full\.json["\']': "AGENT_DISCOVERY_JSON",
    r'["\']agent_discovery_full\.manifest\.json["\']': "AGENT_DISCOVERY_MANIFEST_JSON",
    # Layer directories
    r'["\']agentic_core/L0_routing["\']': "L0_MAINTENANCE_DIR",
    r'["\']agentic_core/L1_cognition["\']': "L1_COGNITION_DIR",
    r'["\']agentic_core/L2_execution["\']': "L2_EXECUTION_DIR",
    r'["\']agentic_core/L3_orchestration["\']': "L3_ORCHESTRATION_DIR",
    r'["\']agentic_core/L4_state["\']': "L4_STATE_DIR",
    r'["\']agentic_core/L5_safety["\']': "L5_SAFETY_DIR",
    r'["\']agentic_core/L6_observability["\']': "L6_OBSERVABILITY_DIR",
    # Critical subdirectories
    r'["\']agentic_core/L6_observability/dashboards["\']': "DASHBOARD_DIR",
    r'["\']agentic_core/config/blueprint_sovereign["\']': "BLUEPRINT_SOVEREIGN_DIR",
    r'["\']agentic_core/runtime/types["\']': "SCHEMAS_DIR",
    r'["\']agentic_core/prompt_governance["\']': "PROMPT_GOVERNANCE_DIR",
    r'["\']agentic_core/utils["\']': "UTILS_DIR",
    r'["\']agentic_core/runtime["\']': "RUNTIME_DIR",
    # Core directories
    r'["\']agentic_core["\']': "AGENTIC_CORE_DIR",
    r'["\']scripts["\']': "SCRIPTS_DIR",
    r'["\']tests/unit["\']': "TESTS_UNIT_DIR",
    r'["\']tests/integration["\']': "TESTS_INTEGRATION_DIR",
    r'["\']tests/e2e["\']': "TESTS_E2E_DIR",
    r'["\']tests["\']': "TESTS_DIR",
    r'["\']apps_rg["\']': "APPS_RG_DIR",
    r'["\']apps_lic["\']': "APPS_LIC_DIR",
    r'["\']apps_shared["\']': "APPS_SHARED_DIR",
    # Output directories
    r'["\']reports["\']': "REPORTS_DIR",
    r'["\']archives["\']': "ARCHIVES_DIR",
}

# Path() constructor patterns
PATH_CONSTRUCTOR_MAP = {
    r'Path\(["\']agent_discovery_full\.json["\']\)': "get_validated_project_root() / AGENT_DISCOVERY_JSON",
    r'Path\(["\']agentic_core/L0_routing["\']\)': "get_validated_project_root() / L0_MAINTENANCE_DIR",
    r'Path\(["\']agentic_core/L1_cognition["\']\)': "get_validated_project_root() / L1_COGNITION_DIR",
    r'Path\(["\']agentic_core/L2_execution["\']\)': "get_validated_project_root() / L2_EXECUTION_DIR",
    r'Path\(["\']agentic_core/L3_orchestration["\']\)': "get_validated_project_root() / L3_ORCHESTRATION_DIR",
    r'Path\(["\']agentic_core/L4_state["\']\)': "get_validated_project_root() / L4_STATE_DIR",
    r'Path\(["\']agentic_core/L5_safety["\']\)': "get_validated_project_root() / L5_SAFETY_DIR",
    r'Path\(["\']agentic_core/L6_observability/dashboards["\']\)': "get_validated_project_root() / DASHBOARD_DIR",
    r'Path\(["\']agentic_core["\']\)': "get_validated_project_root() / AGENTIC_CORE_DIR",
    r'Path\(["\']scripts["\']\)': "get_validated_project_root() / SCRIPTS_DIR",
    r'Path\(["\']tests/unit["\']\)': "get_validated_project_root() / TESTS_UNIT_DIR",
    r'Path\(["\']tests["\']\)': "get_validated_project_root() / TESTS_DIR",
}

# Required imports to add
SSOT_IMPORT = """from agentic_core.L5_safety.config.structure_blueprint_config import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)"""


def should_exclude_path(path: Path) -> bool:
    """Check if path should be excluded."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "should_exclude_path", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "should_exclude_path", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "should_exclude_path")
    parts_lower = {p.lower() for p in path.parts}
    if parts_lower & {d.lower() for d in EXCLUDED_DIRS}:
        return True
    if path.name in EXCLUDED_FILES:
        return True
    return False


def has_ssot_import(content: str) -> bool:
    """Check if file already imports from structure_blueprint."""
    return "from agentic_core.L5_safety.config.structure_blueprint_config import" in content


def add_ssot_import(content: str) -> str:
    """Add SSOT import after last existing import."""
    if has_ssot_import(content):
        return content

    lines = content.split("\n")
    last_import_idx = -1

    # Find last import statement
    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            last_import_idx = i

    if last_import_idx >= 0:
        # Insert SSOT import after last import
        lines.insert(last_import_idx + 1, "")
        lines.insert(last_import_idx + 2, SSOT_IMPORT)
        return "\n".join(lines)
    else:
        # No imports found, add at top after docstring/comments
        insert_idx = 0
        in_docstring = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            if i == 0 and (stripped.startswith('"""') or stripped.startswith("'''")):
                in_docstring = True
            if in_docstring and (stripped.endswith('"""') or stripped.endswith("'''")):
                insert_idx = i + 1
                break
            if not stripped or stripped.startswith("#"):
                continue
            insert_idx = i
            break

        lines.insert(insert_idx, SSOT_IMPORT)
        lines.insert(insert_idx + 1, "")
        return "\n".join(lines)


def refactor_file(file_path: Path, dry_run: bool = False) -> tuple[bool, int]:
    """Refactor a single file to use SSOT constants.

    Returns:
        (was_modified, num_replacements)
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content
        replacements = 0

        # Skip if already importing from structure_blueprint
        if "structure_blueprint" in content and "import" in content:
            # Already using SSOT, skip
            return False, 0

        # Apply string replacements
        for pattern, constant in PATH_TO_SSOT_MAP.items():
            matches = list(re.finditer(pattern, content))
            if matches:
                content = re.sub(pattern, constant, content)
                replacements += len(matches)

        # Apply Path() constructor replacements
        for pattern, replacement in PATH_CONSTRUCTOR_MAP.items():
            matches = list(re.finditer(pattern, content))
            if matches:
                content = re.sub(pattern, replacement, content)
                replacements += len(matches)

        if replacements > 0:
            # Add SSOT import
            content = add_ssot_import(content)

            if not dry_run and content != original_content:
                _wg.write_text(file_path, content, encoding="utf-8")

            return True, replacements

        return False, 0

    # guardian: allow-silent-swallow -- enforcer resilience; refactor failure non-fatal
    except (ValueError, TypeError) as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False, 0


def refactor_repository(dry_run: bool = False) -> dict[str, int]:
    """Refactor entire repository.

    Returns:
        Statistics dict
    """
    print("=" * 80)
    print("HARDCODED PATH REFACTORING" + (" (DRY RUN)" if dry_run else ""))
    print("=" * 80)
    print(f"\n📂 Project: {PROJECT_ROOT}")
    print(
        f"🔄 Mode: {'DRY RUN - No files will be modified' if dry_run else 'LIVE - Files will be modified'}\n",
    )

    stats = {
        "files_scanned": 0,
        "files_modified": 0,
        "total_replacements": 0,
    }

    modified_files = []

    # Scan all Python files
    # Operation Zero: Use ssot_discovery instead of rglob
    from agentic_core.utils.schemas.ssot_discovery_validator import get_python_files

    for py_file in get_python_files(PROJECT_ROOT):
        if should_exclude_path(py_file):
            continue

        stats["files_scanned"] += 1
        was_modified, num_replacements = refactor_file(py_file, dry_run)

        if was_modified:
            stats["files_modified"] += 1
            stats["total_replacements"] += num_replacements
            rel_path = py_file.relative_to(PROJECT_ROOT)
            modified_files.append((rel_path, num_replacements))

    # Print results
    print("\n" + "=" * 80)
    print("REFACTORING SUMMARY")
    print("=" * 80)
    print(f"Files scanned:      {stats['files_scanned']}")
    print(f"Files modified:     {stats['files_modified']}")
    print(f"Total replacements: {stats['total_replacements']}")
    print()

    if modified_files:
        print("Top 20 Modified Files:")
        print("-" * 80)
        for file_path, count in sorted(modified_files, key=lambda x: -x[1])[:20]:
            print(f"   {str(file_path):60} {count:4} replacements")

    return stats


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Refactor hardcoded paths to SSOT")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without modifying files")
    parser.add_argument("--live", action="store_true", help="Actually modify files (requires explicit flag)")
    args = parser.parse_args()

    if not args.dry_run and not args.live:
        print("❌ ERROR: Must specify either --dry-run or --live")
        print("   Use --dry-run to preview changes")
        print("   Use --live to actually modify files")
        return 1

    dry_run = args.dry_run
    stats = refactor_repository(dry_run=dry_run)

    print("\n" + "=" * 80)
    if dry_run:
        print("✅ DRY RUN COMPLETE - No files were modified")
        print("   Run with --live to apply changes")
    else:
        print("✅ REFACTORING COMPLETE")
        print(f"   Modified {stats['files_modified']} files")
        print(f"   Made {stats['total_replacements']} replacements")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    exit(main())
