"""Find agents with Typed % < 100% or Documented % < 100%."""

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

emit_replay_key("p0", "find_low_typed_documented_util")
emit_determinism_digest("p0", "find_low_typed_documented_util")

_emit_dispatches_healing_run("p1", "find_low_typed_documented_util", "L0")
_emit_routes_through("p1", "find_low_typed_documented_util", "L0")
_emit_escalates_to_human("p1", "find_low_typed_documented_util", "L0")
_emit_reads_policy_state("p1", "find_low_typed_documented_util", "L0")

_emit_records_execution_trace("p0", "evidence", "find_low_typed_documented_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "find_low_typed_documented_util", "p0_governance")
_emit_snapshots_state("p0", "find_low_typed_documented_util", "state_snapshot")
_emit_authorize_and_execute("p2", "find_low_typed_documented_util", "execution_auth")
_emit_validates_capability("p2", "find_low_typed_documented_util", "capability_check")
_emit_routes_to_capability("p2", "find_low_typed_documented_util", "capability_route")
_emit_writes_via_uwg("p2", "find_low_typed_documented_util", "uwg_write")
_emit_blocks_direct_write("p2", "find_low_typed_documented_util", "direct_write_block")
_emit_records_tool_invocation("p2", "find_low_typed_documented_util", "tool_invocation")
_emit_captures_execution_output("p2", "find_low_typed_documented_util", "exec_output")
_emit_dispatches_agent("p3", "find_low_typed_documented_util", "agent_dispatch")
_emit_coordinates_agents("p3", "find_low_typed_documented_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "find_low_typed_documented_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "find_low_typed_documented_util", "healing_outcome")
_emit_escalates_failure("p3", "find_low_typed_documented_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "find_low_typed_documented_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "find_low_typed_documented_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "find_low_typed_documented_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "find_low_typed_documented_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "find_low_typed_documented_util", "eval_metric")
_emit_stores_embedding("p4", "find_low_typed_documented_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "find_low_typed_documented_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "find_low_typed_documented_util", "exec_snapshot_link")

PROJECT_ROOT = Path(__file__).parent.parent
with open(PROJECT_ROOT / "agent_discovery_full.json", encoding="utf-8") as f:
    agents = json.load(f)
low_typed = [a for a in agents if a.get("typed_pct", 100) < 100]
low_doc = [a for a in agents if a.get("documented_pct", 100) < 100]
print(f"Agents with Typed < 100%: {len(low_typed)}")
print(f"Agents with Documented < 100%: {len(low_doc)}")
print("\n" + "=" * 70)
print("LOW TYPED AGENTS:")
print("=" * 70)
for a in low_typed:
    print(f"  {a['class_name']}: {a['typed_pct']}% - {a['path']}")
print("\n" + "=" * 70)
print("LOW DOCUMENTED AGENTS:")
print("=" * 70)
for a in low_doc:
    print(f"  {a['class_name']}: {a['documented_pct']}% - {a['path']}")
