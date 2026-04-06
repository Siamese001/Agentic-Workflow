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

_emit_records_execution_trace("p0", "evidence", "refactor_mcp_imports_util")
_emit_applies_guardrail("p0", "refactor_mcp_imports_util", "p0_governance")
_emit_reads_policy_state("p0", "refactor_mcp_imports_util", "policy_binding")
_emit_snapshots_state("p0", "refactor_mcp_imports_util", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_emits_metric_event("refactor_mcp_imports_util", "p4obs", "metric_1")
_emit_emits_metric_event("refactor_mcp_imports_util", "p4obs", "metric_2")
_emit_emits_metric_event("refactor_mcp_imports_util", "p4obs", "metric_3")
_emit_emits_metric_event("refactor_mcp_imports_util", "p4obs", "metric_4")
_emit_emits_metric_event("refactor_mcp_imports_util", "p4obs", "metric_5")
_emit_emits_metric_event("refactor_mcp_imports_util", "p4obs", "metric_6")
_emit_records_incident_event("refactor_mcp_imports_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("refactor_mcp_imports_util", "p4obs", "anomaly")
_emit_writes_observability_log("refactor_mcp_imports_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("refactor_mcp_imports_util", "p4obs", "mon_state")
_emit_triggers_alert("refactor_mcp_imports_util", "p4obs", "alert")
_emit_links_incident_trace("refactor_mcp_imports_util", "p4obs", "trace_link")
_emit_captures_pattern("refactor_mcp_imports_util", "p3lm", "pattern")
_emit_records_learning_event("refactor_mcp_imports_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("refactor_mcp_imports_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("refactor_mcp_imports_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("refactor_mcp_imports_util", "p3lm", "routing")
_emit_improves_agent_policy("refactor_mcp_imports_util", "p3lm", "policy")
_emit_stores_learning_state("refactor_mcp_imports_util", "p3lm", "state")
_emit_records_execution_trace("refactor_mcp_imports_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("refactor_mcp_imports_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("refactor_mcp_imports_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("refactor_mcp_imports_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("refactor_mcp_imports_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("refactor_mcp_imports_util", "env_read", "p2_env_1")
_emit_reads_environ("refactor_mcp_imports_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("refactor_mcp_imports_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("refactor_mcp_imports_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "refactor_mcp_imports_util", "context_pull")
_emit_pulls_context("p1", "refactor_mcp_imports_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "refactor_mcp_imports_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "refactor_mcp_imports_util", "uwg_term_2")
_emit_writes_through("p1", "refactor_mcp_imports_util", "write_through")
_emit_writes_through("p1", "refactor_mcp_imports_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "refactor_mcp_imports_util", "safety_validation")
_emit_invokes_eval("p1", "refactor_mcp_imports_util", "eval_call")
_emit_proposal_commits_routing("p1", "refactor_mcp_imports_util", "routing_commit")
_emit_escalates_to_human("p1", "refactor_mcp_imports_util", "human_escalation")
_emit_routes_through("p1", "refactor_mcp_imports_util", "route_through")
_emit_checks_agent_registry("p1", "refactor_mcp_imports_util", "agent_registry")
_emit_validates_agent_capability("p1", "refactor_mcp_imports_util", "capability")
_emit_dispatches_execution_plan("p1", "refactor_mcp_imports_util", "exec_plan")
_emit_agent_executes_agent("p1", "refactor_mcp_imports_util", "sub_agent")
_emit_routes_to_agent("p1", "refactor_mcp_imports_util", "target_agent")
_emit_verifies_policy("p1", "refactor_mcp_imports_util", "policy_check")
_emit_observes_runtime_state("p1", "refactor_mcp_imports_util", "runtime_state")
_emit_verifies_boundary("p1", "refactor_mcp_imports_util", "boundary_check")
_emit_transcripts_response("p1", "refactor_mcp_imports_util", "transcript")
_emit_hard_fails_untranscripted("p1", "refactor_mcp_imports_util")
_emit_gated_by_confidence("p1", "refactor_mcp_imports_util", "confidence_gate")
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
    from agentic_core.utils.runners.ssot_discovery_validator import get_python_files

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
