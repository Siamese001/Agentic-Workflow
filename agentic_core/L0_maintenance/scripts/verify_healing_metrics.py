#!/usr/bin/env python3
"""
Verify healing and invocation metrics for all agents.
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DISCOVERY_FILE = PROJECT_ROOT / "agent_discovery_full.json"
DASHBOARD_DATA = PROJECT_ROOT / "agentic_core/L6_observability/dashboards/data/dashboard_data.js"


def main():
    """Verify healing metrics."""
    print("=" * 70)
    print("HEALING & INVOCATION METRICS VERIFICATION")
    print("=" * 70)

    # Load agent discovery
    with open(DISCOVERY_FILE, encoding="utf-8") as f:
        agents = json.load(f)

    total = len(agents)
    with_healing = sum(1 for a in agents if a.get("has_healing", False))
    with_invocation = sum(1 for a in agents if a.get("invocation") == "Yes")

    print("\nAgent Discovery Data:")
    print(f"  Total agents: {total}")
    print(f"  With healing: {with_healing} ({with_healing / total * 100:.1f}%)")
    print(f"  With invocation: {with_invocation} ({with_invocation / total * 100:.1f}%)")

    # Load dashboard data
    content = DASHBOARD_DATA.read_text(encoding="utf-8")
    import re

    match = re.search(r"window\.dashboardData = (\[.*?\]);", content, re.DOTALL)
    if match:
        data = json.loads(match.group(1))
        total_row = data[0]

        print("\nDashboard TOTAL Row:")
        print(f"  Heal Cap %: {total_row['Heal Cap %']}")
        print(f"  Invocation %: {total_row['Invocation %']}")
        print(f"  Test %: {total_row['Test %']}")
        print(f"  MCP Hardened %: {total_row['MCP Hardened %']}")
        print(f"  Health Score: {total_row['Health']}")

    print("\n" + "=" * 70)
    if with_healing == total and with_invocation == total:
        print("✅ 100% HEALING AND INVOCATION ACHIEVED")
        print("=" * 70)
        print("\nAll 265 agents have:")
        print("  ✅ Healing capability (has_healing = True)")
        print("  ✅ Invocation capability (invocation = 'Yes')")
    else:
        print("⚠️  NOT AT 100%")
        print("=" * 70)
        print(f"\nMissing healing: {total - with_healing} agents")
        print(f"Missing invocation: {total - with_invocation} agents")


if __name__ == "__main__":
    main()
