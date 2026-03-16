"""
Find agents with open heal invocations.
Open heal invocation = agent has invocation='Yes' but has_healing=False
This is a data integrity issue that needs to be fixed.
"""

import json

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "find_open_heal_invocations_util")
emit_determinism_digest("p0", "find_open_heal_invocations_util")

_emit_dispatches_healing_run("p1", "find_open_heal_invocations_util", "L0")
_emit_routes_through("p1", "find_open_heal_invocations_util", "L0")
_emit_escalates_to_human("p1", "find_open_heal_invocations_util", "L0")
_emit_reads_policy_state("p1", "find_open_heal_invocations_util", "L0")

_emit_records_execution_trace("p0", "evidence", "find_open_heal_invocations_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "find_open_heal_invocations_util", "p0_governance")
_emit_snapshots_state("p0", "find_open_heal_invocations_util", "state_snapshot")

with open("agent_discovery_full.json") as f:
    agents = json.load(f)
print(f"Total agents: {len(agents)}")
open_invocations = []
for agent in agents:
    invocation = agent.get("invocation", "No")
    has_healing = agent.get("has_healing", False)
    if invocation == "Yes" and (not has_healing):
        open_invocations.append(agent)
print(f"\n{'=' * 70}")
print(f"AGENTS WITH OPEN HEAL INVOCATIONS: {len(open_invocations)}")
print(f"{'=' * 70}")
if not open_invocations:
    print("✅ No open heal invocations found - all agents are consistent!")
else:
    by_territory = {}
    for agent in open_invocations:
        territory = agent.get("territory", "Unknown")
        if territory not in by_territory:
            by_territory[territory] = []
        by_territory[territory].append(agent)
    for territory in sorted(by_territory.keys()):
        agents_list = by_territory[territory]
        print(f"\n{territory} ({len(agents_list)} agents):")
        for agent in agents_list:
            print(f"  - {agent['class_name']}")
            print(f"    Path: {agent['path']}")
            print(f"    Invocation: {agent.get('invocation')}")
            print(f"    Has Healing: {agent.get('has_healing')}")
            print(f"    Inheritance: {', '.join(agent.get('inheritance', []))}")
print(f"\n{'=' * 70}")
print("SUMMARY")
print(f"{'=' * 70}")
print(f"Total agents: {len(agents)}")
print(f"Agents with healing: {sum(1 for a in agents if a.get('has_healing'))}")
print(f"Agents with invocation: {sum(1 for a in agents if a.get('invocation') == 'Yes')}")
print(f"Open heal invocations: {len(open_invocations)}")
print("\nExpected: Invocation count should equal Healing count")
print(
    f"Actual gap: {sum(1 for a in agents if a.get('invocation') == 'Yes') - sum(1 for a in agents if a.get('has_healing'))}"
)
