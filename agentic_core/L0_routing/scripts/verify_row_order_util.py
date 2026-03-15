"""Verify dashboard row order"""

import json

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "verify_row_order_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "verify_row_order_util", "p0_governance")
_emit_snapshots_state("p0", "verify_row_order_util", "state_snapshot")

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
