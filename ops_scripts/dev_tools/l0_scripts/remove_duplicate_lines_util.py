#!/usr/bin/env python3
"""
Remove duplicate const realAgentData declarations by line numbers.
"""

# Import SSOT for dashboard directory - NO HARDCODING
from agentic_core.L5_safety.config.structure_blueprint import (
    DASHBOARD_DIR,
    get_validated_project_root,
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

_emit_records_execution_trace("p0", "evidence", "remove_duplicate_lines_util")
_emit_applies_guardrail("p0", "remove_duplicate_lines_util", "p0_governance")
_emit_reads_policy_state("p0", "remove_duplicate_lines_util", "policy_binding")
_emit_snapshots_state("p0", "remove_duplicate_lines_util", "state_snapshot")
emit_replay_key("p0", "remove_duplicate_lines_util")
emit_determinism_digest("p0", "remove_duplicate_lines_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "remove_duplicate_lines_util", "execution_auth")
_emit_validates_capability("p2", "remove_duplicate_lines_util", "capability_check")
_emit_routes_to_capability("p2", "remove_duplicate_lines_util", "capability_route")
_emit_writes_via_uwg("p2", "remove_duplicate_lines_util", "uwg_write")
_emit_blocks_direct_write("p2", "remove_duplicate_lines_util", "direct_write_block")
_emit_records_tool_invocation("p2", "remove_duplicate_lines_util", "tool_invocation")
_emit_captures_execution_output("p2", "remove_duplicate_lines_util", "exec_output")
_emit_dispatches_agent("p3", "remove_duplicate_lines_util", "agent_dispatch")
_emit_coordinates_agents("p3", "remove_duplicate_lines_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "remove_duplicate_lines_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "remove_duplicate_lines_util", "healing_outcome")
_emit_escalates_failure("p3", "remove_duplicate_lines_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "remove_duplicate_lines_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "remove_duplicate_lines_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "remove_duplicate_lines_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "remove_duplicate_lines_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "remove_duplicate_lines_util", "eval_metric")
_emit_stores_embedding("p4", "remove_duplicate_lines_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "remove_duplicate_lines_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "remove_duplicate_lines_util", "exec_snapshot_link")


def remove_duplicates():
    """Remove duplicate realAgentData declarations at specific line numbers."""
    dashboard_path = get_validated_project_root() / DASHBOARD_DIR / "autonomy_dashboard.html"

    print("Reading dashboard HTML...")
    lines = dashboard_path.read_text(encoding="utf-8").splitlines(keepends=True)

    # Line numbers to remove (keep first at 1427, remove others)
    # Convert to 0-indexed
    lines_to_remove_start = [10187 - 1, 18947 - 1, 27567 - 1, 36187 - 1]

    print(f"Total lines: {len(lines)}")
    print(f"Removing duplicate realAgentData declarations at lines: {[l + 1 for l in lines_to_remove_start]}")

    # For each duplicate, find the end of the declaration (the closing };)
    ranges_to_remove = []

    for start_line in lines_to_remove_start:
        # Find the comment line before it
        comment_line = start_line - 1
        if comment_line >= 0 and "Real per-agent data" in lines[comment_line]:
            # Find the closing }; after the declaration
            end_line = start_line
            brace_count = 0
            found_start = False

            for i in range(start_line, min(start_line + 10000, len(lines))):
                line = lines[i]
                if "{" in line:
                    brace_count += line.count("{")
                    found_start = True
                if "}" in line:
                    brace_count -= line.count("}")
                    if found_start and brace_count == 0 and "};" in line:
                        end_line = i
                        break

            ranges_to_remove.append((comment_line, end_line))
            print(f"  Range: lines {comment_line + 1} to {end_line + 1}")

    # Remove ranges in reverse order to preserve indices
    for start, end in reversed(ranges_to_remove):
        del lines[start : end + 1]

    # Write back
    dashboard_path.write_text("".join(lines), encoding="utf-8")
    print(f"✅ Removed {len(ranges_to_remove)} duplicate declarations")
    print(f"   New file has {len(lines)} lines")


if __name__ == "__main__":
    remove_duplicates()
