"""
Identify agents without test coverage for improvement.
Prioritize by layer and complexity.
"""

import json
from collections import defaultdict
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
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
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "identify_agents_without_tests_util")
emit_determinism_digest("p0", "identify_agents_without_tests_util")

_emit_dispatches_healing_run("p1", "identify_agents_without_tests_util", "L0")
_emit_routes_through("p1", "identify_agents_without_tests_util", "L0")
_emit_escalates_to_human("p1", "identify_agents_without_tests_util", "L0")
_emit_reads_policy_state("p1", "identify_agents_without_tests_util", "L0")
_emit_authorize_and_execute("p2", "identify_agents_without_tests_util", "execution_auth")
_emit_validates_capability("p2", "identify_agents_without_tests_util", "capability_check")
_emit_routes_to_capability("p2", "identify_agents_without_tests_util", "capability_route")
_emit_writes_via_uwg("p2", "identify_agents_without_tests_util", "uwg_write")
_emit_blocks_direct_write("p2", "identify_agents_without_tests_util", "direct_write_block")
_emit_records_tool_invocation("p2", "identify_agents_without_tests_util", "tool_invocation")
_emit_captures_execution_output("p2", "identify_agents_without_tests_util", "exec_output")
_emit_dispatches_agent("p3", "identify_agents_without_tests_util", "agent_dispatch")
_emit_coordinates_agents("p3", "identify_agents_without_tests_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "identify_agents_without_tests_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "identify_agents_without_tests_util", "healing_outcome")
_emit_escalates_failure("p3", "identify_agents_without_tests_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "identify_agents_without_tests_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "identify_agents_without_tests_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "identify_agents_without_tests_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "identify_agents_without_tests_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "identify_agents_without_tests_util", "eval_metric")
_emit_stores_embedding("p4", "identify_agents_without_tests_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "identify_agents_without_tests_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "identify_agents_without_tests_util", "exec_snapshot_link")

project_root = Path(__file__).parent.parent
with open(project_root / "agent_discovery_full.json", encoding="utf-8") as f:
    agents = json.load(f)
agents_without_tests = [a for a in agents if not a.get("has_tests", False)]
print(f"\n{'=' * 70}")
print(f"AGENTS WITHOUT TEST COVERAGE: {len(agents_without_tests)}")
print(f"{'=' * 70}\n")
by_territory = defaultdict(list)
for agent in agents_without_tests:
    territory = agent.get("territory", "Unknown")
    by_territory[territory].append(agent)
layer_priority = {
    "L6_Observability": 1,
    "L5 Safety": 2,
    "L4 State": 3,
    "L3 Orchestration": 4,
    "L2 Execution": 5,
    "L1 Cognition": 6,
    "L0 Maintenance": 7,
    "Apps": 8,
    "Utils": 9,
}


def get_priority(territory):
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "get_priority", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "get_priority", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "get_priority")
    for key, priority in layer_priority.items():
        if territory.startswith(key):
            return priority
    return 10


sorted_territories = sorted(by_territory.keys(), key=get_priority)
print("Agents without tests by territory:\n")
for territory in sorted_territories:
    agents_list = by_territory[territory]
    print(f"{territory}: {len(agents_list)} agents")
    for agent in agents_list:
        name = agent.get("class_name", "Unknown")
        path = agent.get("path", "Unknown")
        cc = agent.get("cyclomatic_complexity", 0)
        print(f"  - {name:40} (CC: {cc:2}, Path: {path})")
print(f"\n{'=' * 70}")
print("RECOMMENDED FIRST BATCH (8 agents)")
print(f"{'=' * 70}\n")
base_agents = [a for a in agents_without_tests if "Base Agent" in a.get("territory", "")]
high_layer = [
    a
    for a in agents_without_tests
    if any(
        a.get("territory", "").startswith(layer) for layer in ["L6_Observability", "L5 Safety", "L4 State"]
    )
    and a not in base_agents
]
base_agents.sort(key=lambda a: a.get("cyclomatic_complexity", 0))
high_layer.sort(key=lambda a: a.get("cyclomatic_complexity", 0))
batch1 = (base_agents + high_layer)[:8]
for i, agent in enumerate(batch1, 1):
    name = agent.get("class_name", "Unknown")
    path = agent.get("path", "Unknown")
    territory = agent.get("territory", "Unknown")
    cc = agent.get("cyclomatic_complexity", 0)
    print(f"{i}. {name}")
    print(f"   Territory: {territory}")
    print(f"   Path: {path}")
    print(f"   Complexity: {cc}")
    print(f"   Priority: {('BASE AGENT' if 'Base Agent' in territory else 'High Layer')}")
    print()
print(f"{'=' * 70}")
print("NEXT STEPS")
print(f"{'=' * 70}\n")
print("For each agent:")
print("1. Add SubatomicTestingMixin to inheritance")
print("2. OR implement _run_self_tests() method")
print("3. Verify tests work")
print("4. Re-run agent discovery")
