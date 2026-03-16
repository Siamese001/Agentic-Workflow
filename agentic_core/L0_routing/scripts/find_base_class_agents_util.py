"""Find all agents with 'Base Class' in their territory field."""

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

emit_replay_key("p0", "find_base_class_agents_util")
emit_determinism_digest("p0", "find_base_class_agents_util")

_emit_dispatches_healing_run("p1", "find_base_class_agents_util", "L0")
_emit_routes_through("p1", "find_base_class_agents_util", "L0")
_emit_escalates_to_human("p1", "find_base_class_agents_util", "L0")
_emit_reads_policy_state("p1", "find_base_class_agents_util", "L0")

_emit_records_execution_trace("p0", "evidence", "find_base_class_agents_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "find_base_class_agents_util", "p0_governance")
_emit_snapshots_state("p0", "find_base_class_agents_util", "state_snapshot")
_emit_authorize_and_execute("p2", "find_base_class_agents_util", "execution_auth")
_emit_validates_capability("p2", "find_base_class_agents_util", "capability_check")
_emit_routes_to_capability("p2", "find_base_class_agents_util", "capability_route")
_emit_writes_via_uwg("p2", "find_base_class_agents_util", "uwg_write")
_emit_blocks_direct_write("p2", "find_base_class_agents_util", "direct_write_block")
_emit_records_tool_invocation("p2", "find_base_class_agents_util", "tool_invocation")
_emit_captures_execution_output("p2", "find_base_class_agents_util", "exec_output")
_emit_dispatches_agent("p3", "find_base_class_agents_util", "agent_dispatch")
_emit_coordinates_agents("p3", "find_base_class_agents_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "find_base_class_agents_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "find_base_class_agents_util", "healing_outcome")
_emit_escalates_failure("p3", "find_base_class_agents_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "find_base_class_agents_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "find_base_class_agents_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "find_base_class_agents_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "find_base_class_agents_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "find_base_class_agents_util", "eval_metric")
_emit_stores_embedding("p4", "find_base_class_agents_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "find_base_class_agents_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "find_base_class_agents_util", "exec_snapshot_link")

project_root = Path(__file__).parent.parent
discovery_file = project_root / "agent_discovery_full.json"
with open(discovery_file, encoding="utf-8") as f:
    agents = json.load(f)
base_class_agents = [a for a in agents if "Base Class" in a.get("territory", "")]
print(f"\n{'=' * 70}")
print(f"AGENTS WITH 'Base Class' IN TERRITORY: {len(base_class_agents)}")
print(f"{'=' * 70}\n")
for agent in base_class_agents:
    class_name = agent.get("class_name", "Unknown")
    territory = agent.get("territory", "Unknown")
    path = agent.get("path", "Unknown")
    print(f"Class: {class_name}")
    print(f"  Territory: {territory}")
    print(f"  Path: {path}")
    print()
print(f"{'=' * 70}")
print("TERRITORY NAMES TO FIX")
print(f"{'=' * 70}\n")
territory_mappings = {
    "Base/Base Class": "Sovereign Base Agent",
    "L6_Observability/Base Class": "L6_Observability/Base Agent",
    "L5 Safety/Base Class": "L5 Safety/Base Agent",
    "L4 State/Base Class": "L4 State/Base Agent",
    "L3 Orchestration/Base Class": "L3 Orchestration/Base Agent",
    "L2 Execution/Base Class": "L2 Execution/Base Agent",
    "L1 Cognition/Base Class": "L1 Cognition/Base Agent",
    "L0 Maintenance/Base Class": "L0 Maintenance/Base Agent",
}
for old, new in territory_mappings.items():
    count = sum(1 for a in agents if a.get("territory") == old)
    print(f"{old:40} → {new:40} ({count} agents)")
