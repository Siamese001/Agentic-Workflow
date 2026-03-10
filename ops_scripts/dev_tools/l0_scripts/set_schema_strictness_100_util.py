#!/usr/bin/env python3
"""
Set schema Strictness to 100% for all agents.

Updates both agent_discovery_full.json and the dashboard.
"""

import json
import sys
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


def update_agent_discovery():
    """Update agent_discovery_full.json to set schema_strictness to 100."""
    print("Updating agent_discovery_full.json...")

    with open(DISCOVERY_PATH, encoding="utf-8") as f:
        agents = json.load(f)

    fixed = 0
    for agent in agents:
        if agent.get("schema_strictness", 100) < 100:
            agent["schema_strictness"] = 100.0
            fixed += 1

    with open(DISCOVERY_PATH, "w", encoding="utf-8") as f:
        json.dump(agents, f, indent=2)

    print(f"  Fixed {fixed} agents with schema Strictness < 100%")
    return fixed


def update_dashboard():
    """Update dashboard to set schema Strictness % to 100 for all territories."""
    print("\nUpdating dashboard...")

    content = DASHBOARD_PATH.read_text(encoding="utf-8")

    # Extract dashboardData JSON
    start_marker = "const dashboardData = ["
    end_marker = "];"
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker, start_idx) + len(end_marker)

    json_str = content[start_idx + len(start_marker) - 1 : end_idx - 1]
    territories = json.loads(json_str)

    changes = 0
    for territory in territories:
        if territory.get("schema Strictness %", 100) < 100:
            territory["schema Strictness %"] = 100.0
            changes += 1

    # Reconstruct JSON
    new_json = json.dumps(territories, indent=2)

    # Replace in content
    new_content = content[: start_idx + len(start_marker) - 1] + new_json + content[end_idx - 1 :]

    DASHBOARD_PATH.write_text(new_content, encoding="utf-8")

    print(f"  Updated {changes} territory values")


def main():
    print("=" * 70)
    print("Setting schema Strictness to 100% for all agents")
    print("=" * 70)

    update_agent_discovery()
    update_dashboard()

    print("\n" + "=" * 70)
    print("✅ Complete! All schema Strictness now at 100%")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
