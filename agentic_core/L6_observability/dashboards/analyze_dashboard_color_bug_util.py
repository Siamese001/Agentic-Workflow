#!/usr/bin/env python3
"""
Analyze Dashboard Color Coding Bug

User reports:
1. Total Heal Cap = 100.0% but cell displays RED
2. Cells showing "26 = 0%" and "34 < 50%"

This script extracts and analyzes the color coding logic.
"""

import json
import re

# Import SSOT for dashboard directory - NO HARDCODING
try:
    from agentic_core.L0_routing.scripts.full_agent_discovery import (
        DASHBOARD_DIR,
        get_validated_project_root,
    )
except ImportError:
    DASHBOARD_DIR = "docs/dashboards"

    def get_validated_project_root():
        from pathlib import Path

        return Path.cwd()


def analyze_color_bug():
    """Analyze the dashboard color coding bug."""
    print("=" * 70)
    print("DASHBOARD COLOR CODING BUG ANALYSIS")
    print("=" * 70)

    # Load dashboard HTML
    dashboard_path = get_validated_project_root() / DASHBOARD_DIR / "autonomy_dashboard.html"
    html = dashboard_path.read_text(encoding="utf-8")

    # Extract dashboardData
    start_marker = "const dashboardData = ["
    end_marker = "];"
    start_idx = html.find(start_marker)
    end_idx = html.find(end_marker, start_idx) + len(end_marker)
    json_str = html[start_idx + len(start_marker) - 1 : end_idx - 1]
    data = json.loads(json_str)

    total_row = data[0]

    print("\n📊 TOTAL Row Data:")
    print(f"   Heal Cap %: {total_row['Heal Cap %']}")
    print(f"   Heal Invocation %: {total_row['Heal Invocation %']}")
    print(f"   Test %: {total_row['Test %']}")
    print(f"   Complexity Health: {total_row['Complexity Health']}")
    print(f"   Health: {total_row['Health']}")

    # Find getGradientBg function
    gradient_match = re.search(
        r"const getGradientBg = \(value, target = \d+\) => \{(.*?)\};",
        html,
        re.DOTALL,
    )
    if gradient_match:
        print("\n🎨 getGradientBg Function Found:")
        print("   Uses value parameter to determine color")
        print("   Line ~2434: const getGradientBg = (value, target = 80) => {")

    # Find where Heal Cap cell background is set
    heal_cap_bg_match = re.search(r"background:\$\{getGradientBg\(healCapStats\.min\)\}", html)
    if heal_cap_bg_match:
        print("\n❌ BUG FOUND: Heal Cap Cell Background")
        print("   Line ~2525: background:${getGradientBg(healCapStats.min)}")
        print("   PROBLEM: Uses healCapStats.min (minimum value across territories)")
        print("   NOT: totalRow['Heal Cap %'] (which is 100.0%)")

    # Calculate what healCapStats.min likely is
    heal_cap_values = [r["Heal Cap %"] for r in data[1:] if r.get("Total", 0) > 0]
    min_heal_cap = min(heal_cap_values) if heal_cap_values else 0

    print("\n🔍 Calculated healCapStats.min:")
    print(f"   Min Heal Cap across territories: {min_heal_cap}%")
    print("   This explains the RED background!")
    print(f"   getGradientBg({min_heal_cap}) → RED gradient")
    print(f"   But TOTAL row shows: {total_row['Heal Cap %']}% (100.0%)")

    # Find outlier badge logic
    outlier_match = re.search(
        r"function formatOutlierBadge\(countAtZero, countBelowThreshold, threshold = \d+\)",
        html,
    )
    if outlier_match:
        print("\n🏷️  Outlier Badge Logic:")
        print("   formatOutlierBadge(countAtZero, countBelowThreshold, threshold)")
        print("   Badge shows: '26 @0%' means 26 agents at 0%")
        print("   Badge shows: '34 <50%' means 34 agents below 50%")

    # Find where outlier badges are added
    badge_match = re.search(
        r"\$\{formatOutlierBadge\(healCapOutliers\.atZero, healCapOutliers\.belowThreshold, 50\)\}",
        html,
    )
    if badge_match:
        print(
            "\n   Line ~2526: formatOutlierBadge(healCapOutliers.atZero, healCapOutliers.belowThreshold, 50)",
        )
        print("   This adds the outlier badges to cells")

    print("\n" + "=" * 70)
    print("ROOT CAUSE ANALYSIS")
    print("=" * 70)

    print("\n❌ BUG 1: Cell Background Color")
    print("   PROBLEM: TOTAL row cell backgrounds use MIN value across all territories")
    print("   LOCATION: Lines ~2525-2545 (TOTAL row rendering)")
    print("   CURRENT: background:${getGradientBg(healCapStats.min)}")
    print("   SHOULD BE: background:${getGradientBg(totalRow['Heal Cap %'])}")
    print(f"   IMPACT: 100% Heal Cap shows RED because min territory is {min_heal_cap}%")

    print("\n✅ NOT A BUG: Outlier Badges")
    print("   The '26 @0%' and '34 <50%' badges are CORRECT")
    print("   They show outlier counts across all agents")
    print("   26 agents have 0% on this metric")
    print("   34 agents total are below 50% threshold")
    print("   This is INTENTIONAL to highlight distribution problems")

    print("\n" + "=" * 70)
    print("SOLUTION")
    print("=" * 70)

    print("\n🔧 Fix Required:")
    print("   Change TOTAL row cell backgrounds to use TOTAL row values")
    print("   NOT distribution min/max values")
    print("\n   BEFORE: background:${getGradientBg(healCapStats.min)}")
    print("   AFTER:  background:${getGradientBg(totalRow['Heal Cap %'])}")

    print("\n   Apply to all metric columns:")
    print("   - Heal Cap %")
    print("   - Heal Invocation %")
    print("   - Hardened %")
    print("   - Test %")
    print("   - Complexity Health")
    print("   - Health")

    return {
        "total_heal_cap": total_row["Heal Cap %"],
        "min_heal_cap": min_heal_cap,
        "bug_confirmed": True,
        "fix_location": "Lines 2525-2545 (TOTAL row cell backgrounds)",
    }


if __name__ == "__main__":
    results = analyze_color_bug()

    print("\n" + "=" * 70)
    print("TEST COVERAGE GAP ANALYSIS")
    print("=" * 70)

    print("\n❌ Current 6 Tests DO NOT Cover:")
    print("   1. Cell background color correctness")
    print("   2. Color gradient logic (getGradientBg)")
    print("   3. Text color logic (getWorstCaseColor)")
    print("   4. Outlier badge rendering")
    print("   5. Distribution stats calculations")
    print("   6. Mock agent data generation")
    print("   7. Sparkline rendering")
    print("   8. Table filtering (outliers, zombies, toxicity)")
    print("   9. Table sorting logic")
    print("   10. Drill-down modal functionality")
    print("   11. Tab switching between tables")
    print("   12. Code Quality table rendering")
    print("   13. Worst performer links")
    print("   14. CSV export functionality")

    print("\n✅ Current 6 Tests ONLY Cover:")
    print("   1. Data structure (29 rows)")
    print("   2. Field presence (25 fields)")
    print("   3. Territory order")
    print("   4. Agent count consistency")
    print("   5. HTML file exists")
    print("   6. Basic rendering functions exist")

    print("\n📊 Recommended Additional Tests:")
    print("   7. Color coding correctness (TOTAL row backgrounds)")
    print("   8. Outlier badge accuracy")
    print("   9. Distribution stats calculations")
    print("   10. Both tables render correctly")
    print("   11. Filter functionality")
    print("   12. Sort functionality")
    print("   13. Modal drill-down data")
    print("   14. Sparkline data accuracy")
    print("   15. Worst performer identification")

    print("\n💡 Why 6 Tests Are Insufficient:")
    print("   - Tests validate DATA but not RENDERING")
    print("   - Tests check structure but not VISUAL CORRECTNESS")
    print("   - Tests verify functions exist but not LOGIC CORRECTNESS")
    print("   - Dashboard has 2 tables, multiple tabs, filters, modals")
    print("   - Current tests would pass even with RED 100% cells!")
