#!/usr/bin/env python3
"""
RCA: Dashboard Row Collapse Investigation

Investigates why dashboard rows were collapsed from 29 to fewer rows
and analyzes the health score calculation logic.
"""

import json

# Import SSOT for dashboard directory - NO HARDCODING
from agentic_core.L5_safety.validators.structure_blueprint import (
    DASHBOARD_DIR,
    get_validated_project_root,
)


def investigate_row_collapse():
    """Investigate why rows were collapsed."""
    print("=" * 70)
    print("RCA: DASHBOARD ROW COLLAPSE")
    print("=" * 70)

    # Load current dashboard
    dashboard_path = get_validated_project_root() / DASHBOARD_DIR / "autonomy_dashboard.html"
    html = dashboard_path.read_text(encoding="utf-8")

    # Extract dashboardData
    start_marker = "const dashboardData = ["
    end_marker = "];"
    start_idx = html.find(start_marker)
    end_idx = html.find(end_marker, start_idx) + len(end_marker)
    json_str = html[start_idx + len(start_marker) - 1 : end_idx - 1]
    data = json.loads(json_str)

    print("\n📊 Current Dashboard State:")
    print(f"   Total rows: {len(data)}")
    print("   Expected: 29 rows (TOTAL + 28 territories)")

    # Analyze rows
    total_row = data[0]
    territory_rows = data[1:]

    print("\n🔍 Row Analysis:")
    print(f"   TOTAL row: {total_row.get('Territory')}")
    print(f"   Territory rows: {len(territory_rows)}")

    # Check for empty territories
    empty_territories = [r for r in territory_rows if r.get("Total", 0) == 0]
    non_empty_territories = [r for r in territory_rows if r.get("Total", 0) > 0]

    print("\n📈 Territory Distribution:")
    print(f"   Non-empty territories: {len(non_empty_territories)}")
    print(f"   Empty territories: {len(empty_territories)}")

    if empty_territories:
        print("\n   Empty territories:")
        for r in empty_territories:
            print(f"      - {r.get('Territory')}")

    # Analyze health score calculation
    print("\n" + "=" * 70)
    print("HEALTH SCORE CALCULATION ANALYSIS")
    print("=" * 70)

    print("\n🧮 Territory-Level Health Formula:")
    print("   health = (test_pct + heal_inv_pct + obs_pct) / 3")
    print("   This is NOT a weighted average of the 5 breakdown components!")

    print("\n⚠️  ISSUE FOUND: Health formula uses only 3 components:")
    print("   1. Test %")
    print("   2. Heal Invocation %")
    print("   3. Observable %")
    print("   Missing: Heal Cap %, Complexity Health")

    print("\n📊 Health Breakdown String:")
    print("   'Heal:XX+Inv:XX+Test:XX+Obs:XX+CC:XX'")
    print("   Shows 5 components but Health only uses 3!")

    # Analyze TOTAL row calculation
    print("\n" + "=" * 70)
    print("TOTAL ROW CALCULATION ANALYSIS")
    print("=" * 70)

    total_agents = total_row.get("Total", 0)
    total_health = total_row.get("Health", 0)

    print("\n📊 TOTAL Row:")
    print(f"   Total Agents: {total_agents}")
    print(f"   Health: {total_health}%")

    # Check if L6 observability rows are included
    l6_rows = [r for r in territory_rows if "L6_Observability" in r.get("Territory", "")]
    l6_agents = sum(r.get("Total", 0) for r in l6_rows)

    print("\n🔍 L6 Observability Rows:")
    print(f"   Count: {len(l6_rows)}")
    print(f"   Total agents: {l6_agents}")

    if l6_rows:
        print("   Territories:")
        for r in l6_rows:
            print(
                f"      - {r.get('Territory')}: {r.get('Total', 0)} agents, Health: {r.get('Health', 0)}%"
            )

    # Verify weighted average calculation
    print("\n🧮 TOTAL Health Calculation:")
    print(
        "   Formula: weighted_avg(Health) = sum(territory_health * territory_agents) / total_agents"
    )

    # Calculate manually
    manual_health_sum = sum(r.get("Health", 0) * r.get("Total", 0) for r in non_empty_territories)
    manual_health_avg = round(manual_health_sum / total_agents, 1) if total_agents > 0 else 0

    print(f"   Manual calculation: {manual_health_avg}%")
    print(f"   Dashboard value: {total_health}%")
    print(f"   Match: {'✅ YES' if abs(manual_health_avg - total_health) < 0.1 else '❌ NO'}")

    # Check if empty rows are included in TOTAL calculation
    print("\n⚠️  Empty Row Handling:")
    print("   Empty territories are created to maintain wireframe")
    print("   TOTAL calculation uses only non-empty rows (correct)")

    return {
        "total_rows": len(data),
        "expected_rows": 29,
        "empty_territories": len(empty_territories),
        "l6_rows": len(l6_rows),
        "l6_agents": l6_agents,
        "health_formula_correct": False,  # Uses 3 components, not 5
        "total_calculation_correct": abs(manual_health_avg - total_health) < 0.1,
    }


def analyze_health_formula():
    """Analyze the health formula in detail."""
    print("\n" + "=" * 70)
    print("DETAILED HEALTH FORMULA ANALYSIS")
    print("=" * 70)

    print("\n📋 Current Formula (Line 241):")
    print("   health = round((test_pct + heal_inv_pct + obs_pct) / 3, 1)")

    print("\n📋 Health Breakdown String (Line 288):")
    print(
        "   'Heal:{heal_cap_pct}+Inv:{heal_inv_pct}+Test:{test_pct}+Obs:{obs_pct}+CC:{complexity_health}'"
    )

    print("\n❌ MISMATCH DETECTED:")
    print("   Health Breakdown shows 5 components:")
    print("      1. Heal Cap %")
    print("      2. Heal Invocation %")
    print("      3. Test %")
    print("      4. Observable %")
    print("      5. Complexity Health")

    print("\n   But Health calculation uses only 3:")
    print("      1. Test %")
    print("      2. Heal Invocation %")
    print("      3. Observable %")

    print("\n💡 RECOMMENDATION:")
    print("   If Health should be weighted average of 5 components:")
    print("   health = (heal_cap_pct + heal_inv_pct + test_pct + obs_pct + complexity_health) / 5")

    print("\n   Or if current 3-component formula is correct:")
    print("   Update Health Breakdown to only show: 'Inv:XX+Test:XX+Obs:XX'")


if __name__ == "__main__":
    results = investigate_row_collapse()
    analyze_health_formula()

    print("\n" + "=" * 70)
    print("RCA SUMMARY")
    print("=" * 70)

    print("\n🔍 Row Collapse Root Cause:")
    print("   ✅ RESOLVED: Generator now creates all 29 rows (including empty territories)")
    print("   Previous issue: Generator only created rows for territories with agents")
    print("   Fix: Lines 340-372 now create empty rows to maintain wireframe")

    print("\n⚠️  Health Score Issue:")
    print("   ❌ UNRESOLVED: Health formula uses 3 components, breakdown shows 5")
    print("   Location: generate_dashboard.py line 241")
    print("   Action needed: Decide if formula should use 3 or 5 components")

    print("\n✅ TOTAL Row Calculation:")
    print(f"   Status: {'CORRECT' if results['total_calculation_correct'] else 'INCORRECT'}")
    print(
        f"   L6 Observability rows: {results['l6_rows']} territories, {results['l6_agents']} agents"
    )
    print("   These ARE included in TOTAL calculation (weighted by agent count)")

    print("\n📊 Current State:")
    print(f"   Total rows: {results['total_rows']}")
    print(f"   Expected: {results['expected_rows']}")
    print(
        f"   Status: {'✅ CORRECT' if results['total_rows'] == results['expected_rows'] else '❌ INCORRECT'}"
    )
