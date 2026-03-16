"""Debug drill-down data structure"""

import json
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

emit_replay_key("p0", "debug_drilldown_util")
emit_determinism_digest("p0", "debug_drilldown_util")

_emit_dispatches_healing_run("p1", "debug_drilldown_util", "L0")
_emit_routes_through("p1", "debug_drilldown_util", "L0")
_emit_escalates_to_human("p1", "debug_drilldown_util", "L0")
_emit_reads_policy_state("p1", "debug_drilldown_util", "L0")

_emit_records_execution_trace("p0", "evidence", "debug_drilldown_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "debug_drilldown_util", "p0_governance")
_emit_snapshots_state("p0", "debug_drilldown_util", "state_snapshot")
_emit_authorize_and_execute("p2", "debug_drilldown_util", "execution_auth")
_emit_validates_capability("p2", "debug_drilldown_util", "capability_check")
_emit_routes_to_capability("p2", "debug_drilldown_util", "capability_route")
_emit_writes_via_uwg("p2", "debug_drilldown_util", "uwg_write")
_emit_blocks_direct_write("p2", "debug_drilldown_util", "direct_write_block")
_emit_records_tool_invocation("p2", "debug_drilldown_util", "tool_invocation")
_emit_captures_execution_output("p2", "debug_drilldown_util", "exec_output")
_emit_dispatches_agent("p3", "debug_drilldown_util", "agent_dispatch")
_emit_coordinates_agents("p3", "debug_drilldown_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "debug_drilldown_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "debug_drilldown_util", "healing_outcome")
_emit_escalates_failure("p3", "debug_drilldown_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "debug_drilldown_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "debug_drilldown_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "debug_drilldown_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "debug_drilldown_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "debug_drilldown_util", "eval_metric")
_emit_stores_embedding("p4", "debug_drilldown_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "debug_drilldown_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "debug_drilldown_util", "exec_snapshot_link")

html = Path("reports/autonomy_dashboard.html").read_text(encoding="utf-8")
data_start = html.find("const dashboardData = ")
data_end = html.find("];", data_start)
data_str = html[data_start + 22 : data_end + 1]
dashboard_data = json.loads(data_str)
for row in dashboard_data[:5]:
    territory = row.get("Territory", "Unknown")
    agents = row.get("agents", [])
    print(f"\nTerritory: {territory}")
    print(f"  Total field: {row.get('Total', 0)}")
    print(f"  Agents array length: {len(agents)}")
    if agents:
        print(f"  First agent keys: {list(agents[0].keys())[:5]}")
    else:
        print("  NO AGENTS DATA!")
print("\n" + "=" * 50)
print("Checking L0 Maintenance territories:")
for row in dashboard_data:
    territory = row.get("Territory", "")
    if "L0" in territory or "Maintenance" in territory:
        agents = row.get("agents", [])
        print(f"\n  {territory}:")
        print(f"    Total: {row.get('Total', 0)}")
        print(f"    Agents: {len(agents)}")
        if agents:
            print(f"    Sample agent: {agents[0].get('rel', 'N/A')}")
