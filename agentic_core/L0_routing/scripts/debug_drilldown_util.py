"""Debug drill-down data structure"""

import json
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "debug_drilldown_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "debug_drilldown_util", "p0_governance")
_emit_snapshots_state("p0", "debug_drilldown_util", "state_snapshot")

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
