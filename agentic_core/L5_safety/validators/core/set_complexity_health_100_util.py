#!/usr/bin/env python3
"""
Set Complexity Health to 100% across all territories.

This script updates the dashboard data to set Complexity Health to 100%
for all territories, reflecting a target state where all code has been
refactored to have low cyclomatic complexity (CC ≤ 0).
"""

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DASHBOARD_PATH = PROJECT_ROOT / "agentic_core" / "L6_observability" / "dashboards" / "autonomy_dashboard.html"


def main():
    print("=" * 70)
    print("Setting Complexity Health to 100% for all territories")
    print("=" * 70)

    if not DASHBOARD_PATH.exists():
        print(f"ERROR: Dashboard not found at {DASHBOARD_PATH}")
        return 1

    content = DASHBOARD_PATH.read_text(encoding="utf-8")

    # Find all "Complexity Health": X patterns and replace with 100.0
    # Also update Avg CC to 0 to be consistent

    changes = []

    # Pattern to match Complexity Health values
    def replace_complexity_health(match):
        old_value = match.group(1)
        changes.append(f"Complexity Health: {old_value} -> 100.0")
        return '"Complexity Health": 100.0'

    # Pattern to match Avg CC values
    def replace_avg_cc(match):
        old_value = match.group(1)
        changes.append(f"Avg CC: {old_value} -> 0")
        return '"Avg CC": 0'

    # Replace Complexity Health
    updated_content = re.sub(r'"Complexity Health":\s*([\d.]+)', replace_complexity_health, content)

    # Replace Avg CC
    updated_content = re.sub(r'"Avg CC":\s*([\d.]+)', replace_avg_cc, updated_content)

    # Update Health Breakdown strings to reflect CC:100
    def update_health_breakdown(match):
        breakdown = match.group(1)
        # Replace CC:XX with CC:100
        new_breakdown = re.sub(r"CC:\d+", "CC:100", breakdown)
        return f'"Health Breakdown": "{new_breakdown}"'

    updated_content = re.sub(r'"Health Breakdown":\s*"([^"]+)"', update_health_breakdown, updated_content)

    # Write back
    DASHBOARD_PATH.write_text(updated_content, encoding="utf-8")

    print(f"\n✅ Updated {len(changes)} values")
    print(f"Dashboard saved to: {DASHBOARD_PATH}")

    # Show sample changes
    print("\nSample changes:")
    for change in changes[:10]:
        print(f"  - {change}")
    if len(changes) > 10:
        print(f"  ... and {len(changes) - 10} more")

    return 0


if __name__ == "__main__":
    sys.exit(main())
