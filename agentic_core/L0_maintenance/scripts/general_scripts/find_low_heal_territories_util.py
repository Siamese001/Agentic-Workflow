#!/usr/bin/env python3
"""Find territories with low heal capability from dashboard data."""

import json

# Read the dashboard file
with open(
    "C:/Git/Agentic-Workflow/agentic_core/L6_observability/dashboards/autonomy_dashboard.html",
    encoding="utf-8",
) as f:
    data = f.read()

# Extract JSON data
start = data.find("const dashboardData = [")
end = data.find("];", start) + 1
json_str = data[start + 21 : end]

# Parse JSON
territories = json.loads(json_str)

# Find territories with low heal capability
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
