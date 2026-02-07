#!/usr/bin/env python3
"""
RCA: Why tables are not loading after switching to real data

Compare mock data structure vs real data structure to identify mismatch
"""

import json
import re

# Import SSOT for dashboard directory - NO HARDCODING
from agentic_core.L5_safety.config.structure_blueprint_config import (
    DASHBOARD_DIR,
    get_validated_project_root,
)


def rca_table_rendering():
    """Root cause analysis for table rendering failure."""
    print("=" * 70)
    print("RCA: TABLE RENDERING FAILURE")
    print("=" * 70)

    dashboard_path = get_validated_project_root() / DASHBOARD_DIR / "autonomy_dashboard.html"
    html = dashboard_path.read_text(encoding="utf-8")

    # Extract dashboardData
    print("\n1. Extracting dashboardData...")
    dash_match = re.search(r"const dashboardData = (\[.*?\]);", html, re.DOTALL)
    if not dash_match:
        print("   ❌ dashboardData not found")
        return

    data = json.loads(dash_match.group(1))
    print(f"   ✅ dashboardData: {len(data)} rows")

    # Get territory names from dashboardData
    territory_names = [row["Territory"] for row in data if row["Territory"] != "TOTAL"]
    print(f"\n2. Territory names in dashboardData ({len(territory_names)}):")
    for i, name in enumerate(territory_names[:5], 1):
        print(f"   {i}. '{name}'")
    print(f"   ... ({len(territory_names) - 5} more)")

    # Extract realAgentData
    print("\n3. Extracting realAgentData...")
    real_match = re.search(r"const realAgentData = (\{.*?\});", html, re.DOTALL)
    if not real_match:
        print("   ❌ realAgentData not found")
        return

    real_data = json.loads(real_match.group(1))
    real_territories = list(real_data.keys())
    print(f"   ✅ realAgentData: {len(real_territories)} territories")

    print(f"\n4. Territory names in realAgentData ({len(real_territories)}):")
    for i, name in enumerate(real_territories[:5], 1):
        print(f"   {i}. '{name}'")
    print(f"   ... ({len(real_territories) - 5} more)")

    # CRITICAL: Compare territory names
    print("\n5. COMPARING TERRITORY NAMES:")
    print("   " + "=" * 66)

    # Check if names match
    dash_set = set(territory_names)
    real_set = set(real_territories)

    in_dash_not_real = dash_set - real_set
    in_real_not_dash = real_set - dash_set
    matching = dash_set & real_set

    print(f"\n   Matching territories: {len(matching)}")
    print(f"   In dashboardData but NOT in realAgentData: {len(in_dash_not_real)}")
    print(f"   In realAgentData but NOT in dashboardData: {len(in_real_not_dash)}")

    if in_dash_not_real:
        print(
            f"\n   ❌ MISMATCH: {len(in_dash_not_real)} territories in dashboardData have NO realAgentData:",
        )
        for name in sorted(in_dash_not_real)[:10]:
            print(f"      - '{name}'")

    if in_real_not_dash:
        print(f"\n   ⚠️  EXTRA: {len(in_real_not_dash)} territories in realAgentData not in dashboardData:")
        for name in sorted(in_real_not_dash)[:10]:
            print(f"      - '{name}'")

    # Check structure of realAgentData
    print("\n6. Checking realAgentData structure:")
    sample_territory = real_territories[0]
    sample_data = real_data[sample_territory]

    print(f"\n   Sample territory: '{sample_territory}'")
    print(f"   Keys: {list(sample_data.keys())}")

    if "agents" in sample_data:
        print(f"   ✅ Has 'agents' array: {len(sample_data['agents'])} agents")
        if sample_data["agents"]:
            agent = sample_data["agents"][0]
            print(f"   Agent keys: {list(agent.keys())}")
    else:
        print("   ❌ Missing 'agents' array")

    # Check rendering function expectations
    print("\n7. Checking rendering function expectations:")

    # Find where globalAgentData is used
    if "globalAgentData[territory]" in html:
        print("   ✅ Code uses: globalAgentData[territory]")
    if "globalAgentData[territoryName]" in html:
        print("   ✅ Code uses: globalAgentData[territoryName]")
    if "globalAgentData[row.Territory]" in html:
        print("   ✅ Code uses: globalAgentData[row.Territory]")

    # ROOT CAUSE SUMMARY
    print("\n" + "=" * 70)
    print("ROOT CAUSE ANALYSIS")
    print("=" * 70)

    if len(in_dash_not_real) > 0:
        print("\n❌ CRITICAL ISSUE FOUND:")
        print(f"   {len(in_dash_not_real)} territories in dashboardData have NO corresponding realAgentData")
        print("\n   IMPACT:")
        print("   - When rendering tries to access globalAgentData[territory]")
        print("   - It gets undefined for these territories")
        print("   - This causes rendering to fail or show empty tables")
        print("\n   SOLUTION:")
        print("   - Territory names in dashboardData MUST match realAgentData keys")
        print("   - Regenerate dashboard to ensure name consistency")
        print("\n   Example mismatches:")
        for name in sorted(in_dash_not_real)[:5]:
            # Find closest match in realAgentData
            closest = None
            for real_name in real_territories:
                if name.lower() in real_name.lower() or real_name.lower() in name.lower():
                    closest = real_name
                    break
            if closest:
                print(f"      dashboardData: '{name}'")
                print(f"      realAgentData: '{closest}' (possible match)")
            else:
                print(f"      dashboardData: '{name}' (no match found)")
    else:
        print("\n✅ Territory names match between dashboardData and realAgentData")
        print("\n   Other possible issues:")
        print("   - Check browser console for JavaScript errors")
        print("   - Verify loadData() is being called")
        print("   - Check if DOM elements exist (kpiGrid, codeQualityGrid)")


if __name__ == "__main__":
    rca_table_rendering()
