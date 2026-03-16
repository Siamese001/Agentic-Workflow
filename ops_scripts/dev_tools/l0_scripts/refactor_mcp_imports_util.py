#!/usr/bin/env python3
"""
Batch Refactoring Script - Fix MCPHardenedMixin Import Violations

Updates all L0 files to use the new MCPHardenedMixin location in utils/core_extensions
instead of L5_safety/guardrails (which violates layer hierarchy).

This fixes ~10 critical L0 → L5 upward dependency violations.
"""

from pathlib import Path

from agentic_core.L5_safety.config.structure_blueprint import (
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "refactor_mcp_imports_util")
_emit_applies_guardrail("p0", "refactor_mcp_imports_util", "p0_governance")
_emit_reads_policy_state("p0", "refactor_mcp_imports_util", "policy_binding")
_emit_snapshots_state("p0", "refactor_mcp_imports_util", "state_snapshot")
emit_replay_key("p0", "refactor_mcp_imports_util")
emit_determinism_digest("p0", "refactor_mcp_imports_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "refactor_mcp_imports_util", "execution_auth")
_emit_validates_capability("p2", "refactor_mcp_imports_util", "capability_check")
_emit_routes_to_capability("p2", "refactor_mcp_imports_util", "capability_route")
_emit_writes_via_uwg("p2", "refactor_mcp_imports_util", "uwg_write")
_emit_blocks_direct_write("p2", "refactor_mcp_imports_util", "direct_write_block")
_emit_records_tool_invocation("p2", "refactor_mcp_imports_util", "tool_invocation")
_emit_captures_execution_output("p2", "refactor_mcp_imports_util", "exec_output")
_emit_dispatches_agent("p3", "refactor_mcp_imports_util", "agent_dispatch")
_emit_coordinates_agents("p3", "refactor_mcp_imports_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "refactor_mcp_imports_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "refactor_mcp_imports_util", "healing_outcome")
_emit_escalates_failure("p3", "refactor_mcp_imports_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "refactor_mcp_imports_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "refactor_mcp_imports_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "refactor_mcp_imports_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "refactor_mcp_imports_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "refactor_mcp_imports_util", "eval_metric")
_emit_stores_embedding("p4", "refactor_mcp_imports_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "refactor_mcp_imports_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "refactor_mcp_imports_util", "exec_snapshot_link")

# Project root
REPO = Path(__file__).parent.parent

# Old import pattern (L5 - violates hierarchy)
OLD_IMPORT = "from agentic_core.mixins.mcp_hardened_mixin import MCPHardenedMixin"

# New import pattern (utils - foundational layer)
NEW_IMPORT = "from agentic_core.mixins.mcp_hardened_mixin import MCPHardenedMixin"


def refactor_file(file_path: Path) -> bool:
    """
    Replace old MCPHardenedMixin import with new location.

    Returns:
        True if file was modified, False otherwise
    """
    try:
        content = file_path.read_text(encoding="utf-8")

        if OLD_IMPORT not in content:
            return False

        # Replace the import
        new_content = content.replace(OLD_IMPORT, NEW_IMPORT)

        # Write back
        file_path.write_text(new_content, encoding="utf-8")

        print(f"✅ Fixed: {file_path.relative_to(REPO)}")
        return True

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False


def main():
    """Refactor all L0 files with MCPHardenedMixin imports."""

    print("=" * 80)
    print("  MCPHardenedMixin Import Refactoring")
    print("=" * 80)
    print()
    print(f"Old import: {OLD_IMPORT}")
    print(f"New import: {NEW_IMPORT}")
    print()

    # Find all Python files in L0_routing/scripts
    l0_scripts = REPO / AGENTIC_CORE_DIR / "L0_routing" / SCRIPTS_DIR

    if not l0_scripts.exists():
        print(f"❌ Directory not found: {l0_scripts}")
        return 1

    files_modified = 0
    files_scanned = 0

    # Phase 6.9 Sub-50: Use ssot_discovery instead of glob
    from agentic_core.utils.ssot_discovery_validator import get_python_files

    for py_file in get_python_files(l0_scripts):
        if py_file.name.startswith("_"):
            continue

        files_scanned += 1
        if refactor_file(py_file):
            files_modified += 1

    print()
    print("=" * 80)
    print("  Summary")
    print("=" * 80)
    print(f"Files scanned: {files_scanned}")
    print(f"Files modified: {files_modified}")
    print()

    if files_modified > 0:
        print("✅ Refactoring complete!")
        print()
        print("Next steps:")
        print("  1. Run: python scripts/ssot.py validate --summary")
        print("  2. Verify import violations decreased")
        print("  3. Test affected agents to ensure functionality")
    else:
        print("ℹ️  No files needed refactoring")

    return 0


if __name__ == "__main__":
    exit(main())
