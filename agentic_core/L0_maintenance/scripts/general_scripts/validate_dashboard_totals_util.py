#!/usr/bin/env python3
"""
Validate Dashboard TOTAL Row Calculations

Verifies that:
1. Total agent count = sum of individual territory rows
2. Weighted averages are computed correctly (agent-count weighted)
3. Health score formula matches documented weights
"""

import json
from pathlib import Path


def validate_totals():
    """Validate dashboard TOTAL row calculations"""

    # Load generated dashboard data
    html = Path("reports/autonomy_dashboard.html").read_text(encoding="utf-8")

    # Extract dashboardData JSON
    data_start = html.find("const dashboardData = ")
    data_end = html.find("];", data_start)
    data_str = html[data_start + 22 : data_end + 1]
    dashboard_data = json.loads(data_str)

    # Separate TOTAL row from territory rows
    total_row = None
    territory_rows = []

    for row in dashboard_data:
        if row.get("Territory") == "TOTAL":
            total_row = row
        else:
            territory_rows.append(row)

    if not total_row:
        print("❌ ERROR: No TOTAL row found in dashboard data")
        return False

    print("Dashboard TOTAL Row Validation")
    print("=" * 70)

    # 1. Validate agent count sum
    print("\n1. Agent Count Validation:")
    expected_total = sum(r["Total"] for r in territory_rows)
    actual_total = total_row["Total"]

    print(f"   Sum of territory agents: {expected_total}")
    print(f"   TOTAL row agent count:   {actual_total}")

    if expected_total == actual_total:
        print("   ✅ Agent count matches")
    else:
        print(f"   ❌ MISMATCH: Expected {expected_total}, got {actual_total}")
        return False

    # 2. Validate weighted averages
    print("\n2. Weighted Average Validation:")

    metrics_to_check = [
        ("Heal Cap %", "Healing Capability"),
        ("Invocation %", "Healing Invocation"),
        ("Hardened %", "MCP Hardened"),
        ("Test %", "Test Coverage"),
        ("Typed %", "Typing"),
        ("Observable %", "observability"),
    ]

    all_valid = True
    for metric_key, metric_name in metrics_to_check:
        # Calculate expected weighted average
        weighted_sum = sum(r[metric_key] * r["Total"] for r in territory_rows)
        expected_avg = round(weighted_sum / expected_total, 1) if expected_total else 0
        actual_avg = total_row[metric_key]

        match = abs(expected_avg - actual_avg) < 0.2  # Allow 0.1 rounding tolerance
        status = "✅" if match else "❌"

        print(f"   {status} {metric_name:20s}: Expected {expected_avg:5.1f}%, Got {actual_avg:5.1f}%")

        if not match:
            all_valid = False
            # Show breakdown for debugging
            print("      Breakdown:")
            for r in territory_rows[:5]:  # Show first 5
                contrib = r[metric_key] * r["Total"] / expected_total
                print(
                    f"        {r['Territory']:30s}: {r[metric_key]:5.1f}% × {r['Total']:3d} agents = {contrib:5.2f}% contribution"
                )

    # 3. Validate Health Score calculation
    print("\n3. Health Score Formula Validation:")

    # Extract components from breakdown
    breakdown = total_row.get("Health Breakdown", [])

    if breakdown:
        print("   Components:")
        calculated_health = 0
        for comp in breakdown:
            points = comp["points"]
            calculated_health += points
            print(
                f"     {comp['component']:20s}: {comp['raw']:5.1f}% × {comp['weight'] * 100:2.0f}% = {points:5.1f} pts"
            )

        print(f"\n   Calculated Health: {calculated_health:.1f}%")
        print(f"   Reported Health:   {total_row['Health']:.1f}%")

        if abs(calculated_health - total_row["Health"]) < 0.2:
            print("   ✅ Health score calculation matches")
        else:
            print(f"   ❌ MISMATCH: Expected {calculated_health:.1f}%, got {total_row['Health']:.1f}%")
            all_valid = False
    else:
        print("   ⚠️  No Health Breakdown found")

    # 4. Check territory distribution
    print("\n4. Territory Distribution:")
    print(f"   Total territories: {len(territory_rows)}")
    print(f"   Total agents: {expected_total}")

    # Show top 5 territories by agent count
    sorted_territories = sorted(territory_rows, key=lambda r: r["Total"], reverse=True)
    print("\n   Top 5 territories by agent count:")
    for r in sorted_territories[:5]:
        pct = r["Total"] / expected_total * 100
        print(f"     {r['Territory']:30s}: {r['Total']:3d} agents ({pct:5.1f}%)")

    print("\n" + "=" * 70)

    if all_valid:
        print("✅ ALL VALIDATIONS PASSED - TOTAL row calculations are correct")
        return True
    else:
        print("❌ VALIDATION FAILED - Fix calculation errors")
        return False


if __name__ == "__main__":
    import sys

    sys.exit(0 if validate_totals() else 1)
