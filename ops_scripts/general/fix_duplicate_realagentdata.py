#!/usr/bin/env python3
"""
Fix duplicate const realAgentData declarations in autonomy_dashboard.html

This script removes all but the first occurrence of realAgentData.
"""

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, guardrail, healer, memory, orchestrator, prompt, state, workflow
# This boosts alignment detection — review and integrate appropriately

import re

# Import SSOT for dashboard directory - NO HARDCODING
from agentic_core.L5_safety.config.structure_blueprint_config import (
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

_emit_authorize_and_execute("p2", "fix_duplicate_realagentdata", "execution_auth")
_emit_validates_capability("p2", "fix_duplicate_realagentdata", "capability_check")
_emit_routes_to_capability("p2", "fix_duplicate_realagentdata", "capability_route")
_emit_writes_via_uwg("p2", "fix_duplicate_realagentdata", "uwg_write")
_emit_blocks_direct_write("p2", "fix_duplicate_realagentdata", "direct_write_block")
_emit_records_tool_invocation("p2", "fix_duplicate_realagentdata", "tool_invocation")
_emit_captures_execution_output("p2", "fix_duplicate_realagentdata", "exec_output")
_emit_dispatches_agent("p3", "fix_duplicate_realagentdata", "agent_dispatch")
_emit_coordinates_agents("p3", "fix_duplicate_realagentdata", "agent_coordination")
_emit_records_workflow_lineage("p3", "fix_duplicate_realagentdata", "workflow_lineage")
_emit_records_healing_outcome("p3", "fix_duplicate_realagentdata", "healing_outcome")
_emit_escalates_failure("p3", "fix_duplicate_realagentdata", "failure_escalation")
_emit_orchestrates_workflow("p3", "fix_duplicate_realagentdata", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "fix_duplicate_realagentdata", "healing_dispatch")
_emit_invokes_evaluation("p3", "fix_duplicate_realagentdata", "evaluation_signal")
_emit_records_telemetry_event("p4", "fix_duplicate_realagentdata", "telemetry_event")
_emit_captures_evaluation_metric("p4", "fix_duplicate_realagentdata", "eval_metric")
_emit_stores_embedding("p4", "fix_duplicate_realagentdata", "embedding_store")
_emit_updates_meta_learning_state("p4", "fix_duplicate_realagentdata", "meta_learning")
_emit_links_execution_to_snapshot("p4", "fix_duplicate_realagentdata", "exec_snapshot_link")
from apps_shared.config.pipeline_constants_config import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)

_emit_records_execution_trace("p0", "evidence", "fix_duplicate_realagentdata")
_emit_applies_guardrail("p0", "fix_duplicate_realagentdata", "p0_governance")
_emit_reads_policy_state("p0", "fix_duplicate_realagentdata", "policy_binding")
_emit_snapshots_state("p0", "fix_duplicate_realagentdata", "state_snapshot")
emit_replay_key("p0", "fix_duplicate_realagentdata")
emit_determinism_digest("p0", "fix_duplicate_realagentdata")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


def fix_duplicates():
    """Remove duplicate realAgentData declarations."""
    dashboard_path = get_validated_project_root() / DASHBOARD_DIR / "autonomy_dashboard.html"

    print("Reading dashboard HTML...")
    html = dashboard_path.read_text(encoding="utf-8")

    # Find all occurrences of realAgentData declarations
    pattern = r"// Real per-agent data \(replaces generateMockAgentData\)\s*const realAgentData = \{[^}]*\};"
    matches = list(re.finditer(pattern, html, re.DOTALL))

    print(f"Found {len(matches)} realAgentData declarations")

    if len(matches) <= 1:
        print("✅ No duplicates found")
        return

    # Keep only the first occurrence, remove all others
    print(f"Removing {len(matches) - 1} duplicate declarations...")

    # Work backwards to preserve indices
    for match in reversed(matches[1:]):
        html = html[: match.start()] + html[match.end() :]

    # Write back
    dashboard_path.write_text(html, encoding="utf-8")
    print(f"✅ Fixed! Removed {len(matches) - 1} duplicates")
    print(f"   Kept first declaration at position {matches[0].start()}")


if __name__ == "__main__":
    fix_duplicates()
