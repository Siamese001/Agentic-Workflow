#!/usr/bin/env python3
"""Sync dashboard agent count with agent_discovery_full.json."""

import json
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR, get_validated_project_root

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

PROJECT_ROOT = get_validated_project_root()
DISCOVERY_PATH = PROJECT_ROOT / "agent_discovery_full.json"
DASHBOARD_PATH = (
    PROJECT_ROOT / AGENTIC_CORE_DIR / "L6_observability" / "dashboards" / "autonomy_dashboard.html"
)

# Load agent discovery
with open(DISCOVERY_PATH, encoding="utf-8") as f:
    agents = json.load(f)

actual_count = len(agents)
print(f"Agent discovery count: {actual_count}")

# Load dashboard
content = DASHBOARD_PATH.read_text(encoding="utf-8")

# Extract dashboardData JSON
start_marker = "const dashboardData = ["
end_marker = "];"
start_idx = content.find(start_marker)
end_idx = content.find(end_marker, start_idx) + len(end_marker)

json_str = content[start_idx + len(start_marker) - 1 : end_idx - 1]
territories = json.loads(json_str)

# Update TOTAL row
for territory in territories:
    if territory.get("Territory") == "TOTAL":
        old_count = territory.get("Total")
        territory["Total"] = actual_count
        territory["Compliant"] = actual_count
        print(f"Updated TOTAL: {old_count} -> {actual_count}")
        break

# Reconstruct JSON
new_json = json.dumps(territories, indent=2)

# Replace in content
new_content = content[: start_idx + len(start_marker) - 1] + new_json + content[end_idx - 1 :]

DASHBOARD_PATH.write_text(new_content, encoding="utf-8")
print("Dashboard updated!")
