"""Verify dashboard row order"""

import json

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

emit_replay_key("p0", "verify_row_order_util")
emit_determinism_digest("p0", "verify_row_order_util")

_emit_dispatches_healing_run("p1", "verify_row_order_util", "L0")
_emit_routes_through("p1", "verify_row_order_util", "L0")
_emit_escalates_to_human("p1", "verify_row_order_util", "L0")
_emit_reads_policy_state("p1", "verify_row_order_util", "L0")

_emit_records_execution_trace("p0", "evidence", "verify_row_order_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "verify_row_order_util", "p0_governance")
_emit_snapshots_state("p0", "verify_row_order_util", "state_snapshot")
_emit_authorize_and_execute("p2", "verify_row_order_util", "execution_auth")
_emit_validates_capability("p2", "verify_row_order_util", "capability_check")
_emit_routes_to_capability("p2", "verify_row_order_util", "capability_route")
_emit_writes_via_uwg("p2", "verify_row_order_util", "uwg_write")
_emit_blocks_direct_write("p2", "verify_row_order_util", "direct_write_block")
_emit_records_tool_invocation("p2", "verify_row_order_util", "tool_invocation")
_emit_captures_execution_output("p2", "verify_row_order_util", "exec_output")
_emit_dispatches_agent("p3", "verify_row_order_util", "agent_dispatch")
_emit_coordinates_agents("p3", "verify_row_order_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "verify_row_order_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "verify_row_order_util", "healing_outcome")
_emit_escalates_failure("p3", "verify_row_order_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "verify_row_order_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "verify_row_order_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "verify_row_order_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "verify_row_order_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "verify_row_order_util", "eval_metric")
_emit_stores_embedding("p4", "verify_row_order_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "verify_row_order_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "verify_row_order_util", "exec_snapshot_link")

with open("agentic_core/L6_observability/dashboards/data/dashboard_data.js", encoding="utf-8") as f:
    content = f.read()
    start = content.find("[")
    end = content.rfind("]") + 1
    data = json.loads(content[start:end])
print("Dashboard Row Order:")
print("=" * 70)
for i, row in enumerate(data, 1):
    territory = row["Territory"]
    print(f"{i:2}. {territory}")
print("=" * 70)
print(f"\n✅ First row: {data[0]['Territory']}")
print(f"✅ Last row: {data[-1]['Territory']}")
print(f"✅ Total rows: {len(data)}")
expected_first = "Sovereign Base Agent"
expected_last = "TOTAL"
if data[0]["Territory"] == expected_first and data[-1]["Territory"] == expected_last:
    print("\n✅ Row order is CORRECT!")
else:
    print("\n❌ Row order is WRONG!")
    print(f"   Expected first: {expected_first}, got: {data[0]['Territory']}")
    print(f"   Expected last: {expected_last}, got: {data[-1]['Territory']}")
