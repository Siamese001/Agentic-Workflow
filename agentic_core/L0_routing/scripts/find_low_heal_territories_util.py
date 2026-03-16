"""Find territories with low heal capability from dashboard data."""

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

emit_replay_key("p0", "find_low_heal_territories_util")
emit_determinism_digest("p0", "find_low_heal_territories_util")

_emit_dispatches_healing_run("p1", "find_low_heal_territories_util", "L0")
_emit_routes_through("p1", "find_low_heal_territories_util", "L0")
_emit_escalates_to_human("p1", "find_low_heal_territories_util", "L0")
_emit_reads_policy_state("p1", "find_low_heal_territories_util", "L0")

_emit_records_execution_trace("p0", "evidence", "find_low_heal_territories_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "find_low_heal_territories_util", "p0_governance")
_emit_snapshots_state("p0", "find_low_heal_territories_util", "state_snapshot")

with open(
    "C:/Git/Agentic-Workflow/agentic_core/L6_observability/dashboards/autonomy_dashboard.html",
    encoding="utf-8",
) as f:
    data = f.read()
start = data.find("const dashboardData = [")
end = data.find("];", start) + 1
json_str = data[start + 21 : end]
territories = json.loads(json_str)
zero_heal = []
low_heal = []
for t in territories:
    if t["Territory"] == "TOTAL":
        continue
    heal_cap = t.get("Heal Cap %", 100)
    if heal_cap == 0:
        zero_heal.append((t["Territory"], heal_cap, t.get("Total", 0)))
    elif heal_cap < 50:
        low_heal.append((t["Territory"], heal_cap, t.get("Total", 0)))
print(f"=== Territories with 0% Heal Capability ({len(zero_heal)}) ===")
for name, pct, count in zero_heal:
    print(f"  {name}: {pct}% ({count} agents)")
print(f"\n=== Territories with <50% Heal Capability ({len(low_heal)}) ===")
for name, pct, count in sorted(low_heal, key=lambda x: x[1]):
    print(f"  {name}: {pct}% ({count} agents)")
print("\n=== Summary ===")
print(f"Total territories at 0%: {len(zero_heal)}")
print(f"Total territories <50%: {len(low_heal)}")
print(f"Total territories needing fix: {len(zero_heal) + len(low_heal)}")
