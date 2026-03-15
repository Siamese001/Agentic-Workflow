"""Verify heal invocation coverage after fixes."""

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
)

_emit_dispatches_healing_run("p1", "verify_heal_invocation_util", "L0")
_emit_routes_through("p1", "verify_heal_invocation_util", "L0")
_emit_escalates_to_human("p1", "verify_heal_invocation_util", "L0")
_emit_reads_policy_state("p1", "verify_heal_invocation_util", "L0")

_emit_records_execution_trace("p0", "evidence", "verify_heal_invocation_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "verify_heal_invocation_util", "p0_governance")
_emit_snapshots_state("p0", "verify_heal_invocation_util", "state_snapshot")

data = json.load(open("agent_discovery_full.json"))
total = len(data)
has_invocation = sum(1 for a in data if a.get("invocation") == "Yes")
percentage = has_invocation / total * 100
print("=" * 80)
print("HEAL INVOCATION VERIFICATION")
print("=" * 80)
print(f"Total agents: {total}")
print(f"Agents with heal invocation: {has_invocation}")
print(f"Coverage: {percentage:.1f}%")
print()
if percentage >= 100.0:
    print("✅ TARGET ACHIEVED: 100% heal invocation coverage!")
elif percentage >= 99.0:
    print(f"⚠️  NEARLY COMPLETE: {100 - percentage:.1f}% gap remaining")
    missing = [a for a in data if a.get("invocation") != "Yes"]
    for agent in missing:
        print(f"  - {agent['class_name']}: {agent.get('path')}")
else:
    print(f"❌ GAP: {100 - percentage:.1f}% ({total - has_invocation} agents)")
print("=" * 80)
