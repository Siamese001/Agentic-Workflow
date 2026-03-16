"""Debug which territories have mismatched targets."""

import json
import re
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
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

emit_replay_key("p0", "debug_target_mismatch_util")
emit_determinism_digest("p0", "debug_target_mismatch_util")

_emit_dispatches_healing_run("p1", "debug_target_mismatch_util", "L0")
_emit_routes_through("p1", "debug_target_mismatch_util", "L0")
_emit_escalates_to_human("p1", "debug_target_mismatch_util", "L0")
_emit_reads_policy_state("p1", "debug_target_mismatch_util", "L0")

_emit_records_execution_trace("p0", "evidence", "debug_target_mismatch_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "debug_target_mismatch_util", "p0_governance")
_emit_snapshots_state("p0", "debug_target_mismatch_util", "state_snapshot")
_emit_authorize_and_execute("p2", "debug_target_mismatch_util", "execution_auth")
_emit_validates_capability("p2", "debug_target_mismatch_util", "capability_check")
_emit_routes_to_capability("p2", "debug_target_mismatch_util", "capability_route")
_emit_writes_via_uwg("p2", "debug_target_mismatch_util", "uwg_write")
_emit_blocks_direct_write("p2", "debug_target_mismatch_util", "direct_write_block")
_emit_records_tool_invocation("p2", "debug_target_mismatch_util", "tool_invocation")
_emit_captures_execution_output("p2", "debug_target_mismatch_util", "exec_output")
_emit_dispatches_agent("p3", "debug_target_mismatch_util", "agent_dispatch")
_emit_coordinates_agents("p3", "debug_target_mismatch_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "debug_target_mismatch_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "debug_target_mismatch_util", "healing_outcome")
_emit_escalates_failure("p3", "debug_target_mismatch_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "debug_target_mismatch_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "debug_target_mismatch_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "debug_target_mismatch_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "debug_target_mismatch_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "debug_target_mismatch_util", "eval_metric")
_emit_stores_embedding("p4", "debug_target_mismatch_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "debug_target_mismatch_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "debug_target_mismatch_util", "exec_snapshot_link")

dashboard_path = Path("reports/autonomy_dashboard.html")
html = dashboard_path.read_text(encoding="utf-8")
data_match = re.search("const dashboardData = (\\[.*?\\]);", html, re.DOTALL)
rows = json.loads(data_match.group(1))
non_total = [r for r in rows if r.get("Territory") != "TOTAL"]
print("Checking all territories for target mismatches:\n")
mismatches = []
for row in non_total:
    target_inv = row.get("Target Invocation")
    territory = row.get("Territory", "")
    expected = None
    if "L0 Maintenance" in territory:
        if "Infrastructure" in territory or "Infrast" in territory:
            expected = 70
        else:
            expected = 20
    elif "Infrastructure" in territory or "Infrast" in territory:
        expected = 70
    elif "Base Cl" in territory:
        expected = "N/A"
    else:
        expected = 100
    if target_inv != expected:
        mismatches.append((territory, target_inv, expected))
        print(f"❌ {territory}")
        print(f"   Actual: {target_inv}, Expected: {expected}\n")
if not mismatches:
    print("✅ All territories have correct targets!")
else:
    print(f"\nTotal mismatches: {len(mismatches)}")
