#!/usr/bin/env python3
"""Verify Base Agent names in dashboard data."""

import json
from pathlib import Path

project_root = Path(__file__).parent.parent
data_file = (
    project_root / "agentic_core" / "L6_observability" / "dashboards" / "data" / "dashboard_data.js"
)

content = data_file.read_text(encoding="utf-8")
lines = [l for l in content.split("\n") if not l.strip().startswith("//")]
content = "\n".join(lines).replace("window.dashboardData = ", "").strip().rstrip(";")
data = json.loads(content)

print("\nFirst 10 territories in dashboard data:")
print("=" * 60)
for i, row in enumerate(data[:10]):
    print(f"{i + 1}. {row['Territory']}")

print("\n" + "=" * 60)
print("Base Agent territories:")
print("=" * 60)
for row in data:
    if "Base Agent" in row["Territory"] or row["Territory"] == "Sovereign Base Agent":
        print(f"  ✅ {row['Territory']}")
