#!/usr/bin/env python3
"""Debug drill-down data structure"""

import json
from pathlib import Path

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

html = Path("reports/autonomy_dashboard.html").read_text(encoding="utf-8")

# Extract dashboardData JSON
data_start = html.find("const dashboardData = ")
data_end = html.find("];", data_start)
data_str = html[data_start + 22 : data_end + 1]
dashboard_data = json.loads(data_str)

# Check first few rows
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

# Check L0 Maintenance specifically
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
