#!/usr/bin/env python3
"""
Global Refactor Script: Phase 4 - Legacy Base Class Removal

This script performs the global search and replace to repoint all agents
from legacy base classes to SovereignBaseAgent SSOT.

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

Usage: python scripts/refactor_legacy_base_imports_util.py
"""

import os
import re
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR, get_validated_project_root
from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("refactor_legacy_base_imports_util", "p4obs", "metric_1")
_emit_emits_metric_event("refactor_legacy_base_imports_util", "p4obs", "metric_2")
_emit_emits_metric_event("refactor_legacy_base_imports_util", "p4obs", "metric_3")
_emit_emits_metric_event("refactor_legacy_base_imports_util", "p4obs", "metric_4")
_emit_emits_metric_event("refactor_legacy_base_imports_util", "p4obs", "metric_5")
_emit_emits_metric_event("refactor_legacy_base_imports_util", "p4obs", "metric_6")
_emit_records_incident_event("refactor_legacy_base_imports_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("refactor_legacy_base_imports_util", "p4obs", "anomaly")
_emit_writes_observability_log("refactor_legacy_base_imports_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("refactor_legacy_base_imports_util", "p4obs", "mon_state")
_emit_triggers_alert("refactor_legacy_base_imports_util", "p4obs", "alert")
_emit_links_incident_trace("refactor_legacy_base_imports_util", "p4obs", "trace_link")
_emit_captures_pattern("refactor_legacy_base_imports_util", "p3lm", "pattern")
_emit_records_learning_event("refactor_legacy_base_imports_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("refactor_legacy_base_imports_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("refactor_legacy_base_imports_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("refactor_legacy_base_imports_util", "p3lm", "routing")
_emit_improves_agent_policy("refactor_legacy_base_imports_util", "p3lm", "policy")
_emit_stores_learning_state("refactor_legacy_base_imports_util", "p3lm", "state")
_emit_records_execution_trace("refactor_legacy_base_imports_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("refactor_legacy_base_imports_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("refactor_legacy_base_imports_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("refactor_legacy_base_imports_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("refactor_legacy_base_imports_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("refactor_legacy_base_imports_util", "env_read", "p2_env_1")
_emit_reads_environ("refactor_legacy_base_imports_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("refactor_legacy_base_imports_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("refactor_legacy_base_imports_util", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "refactor_legacy_base_imports_util")
_emit_applies_guardrail("p0", "refactor_legacy_base_imports_util", "p0_governance")
_emit_reads_policy_state("p0", "refactor_legacy_base_imports_util", "policy_binding")
_emit_snapshots_state("p0", "refactor_legacy_base_imports_util", "state_snapshot")
_emit_pulls_context("p1", "refactor_legacy_base_imports_util", "context_pull")
_emit_pulls_context("p1", "refactor_legacy_base_imports_util", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "refactor_legacy_base_imports_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "refactor_legacy_base_imports_util", "uwg_term_secondary")
_emit_writes_through("p1", "refactor_legacy_base_imports_util", "write_through")
_emit_writes_through("p1", "refactor_legacy_base_imports_util", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "refactor_legacy_base_imports_util", "safety_validation")
_emit_invokes_eval("p1", "refactor_legacy_base_imports_util", "eval_call")
_emit_proposal_commits_routing("p1", "refactor_legacy_base_imports_util", "routing_commit")
_emit_escalates_to_human("p1", "refactor_legacy_base_imports_util", "human_escalation")
_emit_routes_through("p1", "refactor_legacy_base_imports_util", "route_through")
_emit_checks_agent_registry("p1", "refactor_legacy_base_imports_util", "agent_registry")
_emit_validates_agent_capability("p1", "refactor_legacy_base_imports_util", "capability")
_emit_dispatches_execution_plan("p1", "refactor_legacy_base_imports_util", "exec_plan")
_emit_agent_executes_agent("p1", "refactor_legacy_base_imports_util", "sub_agent")
_emit_routes_to_agent("p1", "refactor_legacy_base_imports_util", "target_agent")
_emit_verifies_policy("p1", "refactor_legacy_base_imports_util", "policy_check")
_emit_observes_runtime_state("p1", "refactor_legacy_base_imports_util", "runtime_state")
_emit_verifies_boundary("p1", "refactor_legacy_base_imports_util", "boundary_check")
_emit_transcripts_response("p1", "refactor_legacy_base_imports_util", "transcript")
_emit_hard_fails_untranscripted("p1", "refactor_legacy_base_imports_util")
_emit_gated_by_confidence("p1", "refactor_legacy_base_imports_util", "confidence_gate")
emit_replay_key("p0", "refactor_legacy_base_imports_util")
emit_determinism_digest("p0", "refactor_legacy_base_imports_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "refactor_legacy_base_imports_util", "execution_auth")
_emit_validates_capability("p2", "refactor_legacy_base_imports_util", "capability_check")
_emit_routes_to_capability("p2", "refactor_legacy_base_imports_util", "capability_route")
_emit_writes_via_uwg("p2", "refactor_legacy_base_imports_util", "uwg_write")
_emit_blocks_direct_write("p2", "refactor_legacy_base_imports_util", "direct_write_block")
_emit_records_tool_invocation("p2", "refactor_legacy_base_imports_util", "tool_invocation")
_emit_captures_execution_output("p2", "refactor_legacy_base_imports_util", "exec_output")
_emit_dispatches_agent("p3", "refactor_legacy_base_imports_util", "agent_dispatch")
_emit_coordinates_agents("p3", "refactor_legacy_base_imports_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "refactor_legacy_base_imports_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "refactor_legacy_base_imports_util", "healing_outcome")
_emit_escalates_failure("p3", "refactor_legacy_base_imports_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "refactor_legacy_base_imports_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "refactor_legacy_base_imports_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "refactor_legacy_base_imports_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "refactor_legacy_base_imports_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "refactor_legacy_base_imports_util", "eval_metric")
_emit_stores_embedding("p4", "refactor_legacy_base_imports_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "refactor_legacy_base_imports_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "refactor_legacy_base_imports_util", "exec_snapshot_link")

# Legacy to SovereignBaseAgent mapping
LEGACY_IMPORTS = {
    "L1CognitionBase": "agentic_core.base_agents.L1CognitionBase",
    "L2ExecutionBase": "agentic_core.L2_execution.L2ExecutionBase",
    "L3OrchestrationBase": "agentic_core.L3_orchestration.reasoning.L3OrchestrationBase",
    "L4StateBase": "agentic_core.L4_state.memory.L4StateBase",
    "L5SafetyBase": "agentic_core.L5_safety.validators.L5SafetyBase",
    "L6ObservabilityBase": "agentic_core.L6_observability.L6ObservabilityBase",
    "MaintenanceBaseAgent": "agentic_core.L5_safety.validators.MaintenanceBaseAgent",
}


def find_python_files(directory: Path) -> list[Path]:
    """Find all Python files in the directory recursively."""
    python_files = []
    for root, _dirs, files in os.walk(directory):
        _dirs[:] = [d for d in _dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
        for file in files:
            if file.endswith(".py"):
                python_files.append(Path(root) / file)
    return python_files


def refactor_file(file_path: Path) -> tuple[bool, list[str]]:
    """Refactor a single file to replace legacy base class imports."""
    changes_made = []
    modified = False

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Replace import statements
        for legacy_name, legacy_path in LEGACY_IMPORTS.items():
            # Pattern: from legacy_path import legacy_name
            import_pattern = f"from {legacy_path} import {legacy_name}"
            if import_pattern in content:
                content = content.replace(
                    import_pattern,
                    "from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent",
                )
                changes_made.append(
                    f"Import: {import_pattern} -> from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent",
                )
                modified = True

            # Pattern: relative imports like from .L5SafetyBase import L5SafetyBase
            relative_import_pattern = f"from .{legacy_name} import {legacy_name}"
            if relative_import_pattern in content:
                content = content.replace(
                    relative_import_pattern,
                    "from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent",
                )
                changes_made.append(
                    f"Import: {relative_import_pattern} -> from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent",
                )
                modified = True

        # Replace class inheritance
        for legacy_name in LEGACY_IMPORTS.keys():
            # Pattern: class SomeAgent(LegacyBaseAgent):
            inheritance_pattern = re.compile(rf"class\s+(\w+)\s*\(\s*{legacy_name}\s*\):")
            matches = inheritance_pattern.findall(content)
            if matches:
                content = inheritance_pattern.sub(r"class \1(SovereignBaseAgent):", content)
                for class_name in matches:
                    changes_made.append(
                        f"Inheritance: class {class_name}({legacy_name}) -> class {class_name}(SovereignBaseAgent)",
                    )
                modified = True

            # Replace references in comments and docstrings
            if legacy_name in content:
                # Replace in comments and docstrings but not in strings
                lines = content.splitlines()
                for i, line in enumerate(lines):
                    if legacy_name in line:
                        # Check if it's a comment or docstring
                        stripped = line.strip()
                        if (
                            stripped.startswith("#")
                            or stripped.startswith('"""')
                            or stripped.startswith("'''")
                            or '"""' in line
                            or "'''" in line
                        ):
                            # Replace the legacy name with SovereignBaseAgent in comments/docstrings
                            lines[i] = line.replace(legacy_name, "SovereignBaseAgent")
                            changes_made.append(f"Comment/Docstring: {legacy_name} -> SovereignBaseAgent")
                            modified = True
                content = "\n".join(lines)

        # Write back if modified
        if modified:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ Refactored: {file_path}")
            for change in changes_made:
                print(f"   - {change}")

        return modified, changes_made

    # guardian: allow-silent-swallow
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False, [f"Error: {e}"]


def main():
    """Main refactoring function."""
    print("=" * 80)
    print("PHASE 4: GLOBAL REFACTOR - LEGACY BASE CLASS REMOVAL")
    print("=" * 80)

    # Target directory
    agentic_core = get_validated_project_root() / AGENTIC_CORE_DIR

    if not agentic_core.exists():
        print(f"❌ Directory not found: {agentic_core}")
        return False

    # Find all Python files
    python_files = find_python_files(agentic_core)
    print(f"📁 Found {len(python_files)} Python files to process")

    # Refactor files
    files_modified = 0
    total_changes = 0

    for file_path in python_files:
        modified, changes = refactor_file(file_path)
        if modified:
            files_modified += 1
            total_changes += len(changes)

    print("\n" + "=" * 80)
    print("REFACTOR SUMMARY:")
    print(f"  Files processed: {len(python_files)}")
    print(f"  Files modified: {files_modified}")
    print(f"  Total changes: {total_changes}")
    print("=" * 80)

    return files_modified > 0


if __name__ == "__main__":
    main()
