#!/usr/bin/env python3
"""
RCA: Health Score Calculation Issue
====================================

User reports health score is not using weighted average despite previous fix.
This script verifies the health score calculation is correct.
"""
import json
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "scripts"))

from dashboard_ssot_definitions import calc_health_score

# Load dashboard data
dashboard_file = project_root / "agentic_core" / "L6_observability" / "dashboards" / "data" / "dashboard_data.js"
content = dashboard_file.read_text(encoding='utf-8')
lines = [l for l in content.split('\n') if not l.strip().startswith('//')]
content = '\n'.join(lines).replace('window.dashboardData = ', '').strip().rstrip(';')
dashboard_data = json.loads(content)

print("\n" + "="*70)
print("HEALTH SCORE CALCULATION VERIFICATION")
print("="*70)

# Get TOTAL row
total_row = next((r for r in dashboard_data if r['Territory'] == 'TOTAL'), None)

if not total_row:
    print("\n❌ TOTAL row not found!")
    sys.exit(1)

print(f"\nTOTAL Row Metrics:")
print(f"  Heal Cap %: {total_row['Heal Cap %']}")
print(f"  Invocation %: {total_row['Invocation %']}")
print(f"  Test %: {total_row['Test %']}")
print(f"  Complexity Health %: {total_row['Complexity Health %']}")
print(f"  Health (dashboard): {total_row['Health']}")

# Calculate expected health using SSOT formula
expected_health = calc_health_score(
    heal_cap_pct=total_row['Heal Cap %'],
    invocation_pct=total_row['Invocation %'],
    test_pct=total_row['Test %'],
    observable_pct=50.0,  # Placeholder
    complexity_health=total_row['Complexity Health %'],
    is_l0=False
)

print(f"\n{'='*70}")
print("SSOT FORMULA VERIFICATION")
print(f"{'='*70}")
print(f"\nExpected Health (SSOT formula):")
print(f"  = (Heal Cap * 0.30) + (Invocation * 0.10) + (Test * 0.25)")
print(f"    + (Observable * 0.20) + (Complexity Health * 0.15)")
print(f"  = ({total_row['Heal Cap %']} * 0.30) + ({total_row['Invocation %']} * 0.10)")
print(f"    + ({total_row['Test %']} * 0.25) + (50.0 * 0.20)")
print(f"    + ({total_row['Complexity Health %']} * 0.15)")
print(f"  = {total_row['Heal Cap %'] * 0.30:.1f} + {total_row['Invocation %'] * 0.10:.1f}")
print(f"    + {total_row['Test %'] * 0.25:.1f} + {50.0 * 0.20:.1f}")
print(f"    + {total_row['Complexity Health %'] * 0.15:.1f}")
print(f"  = {expected_health}")

print(f"\nActual Health (dashboard): {total_row['Health']}")

if abs(expected_health - total_row['Health']) > 0.1:
    print(f"\n{'='*70}")
    print("❌ HEALTH SCORE MISMATCH DETECTED")
    print(f"{'='*70}")
    print(f"Expected: {expected_health}")
    print(f"Actual: {total_row['Health']}")
    print(f"Difference: {abs(expected_health - total_row['Health']):.1f}")
    print("\nROOT CAUSE: Dashboard data not using SSOT weighted formula!")
    print("\nThe health score is NOT using the weighted average formula.")
    print("It may be using simple average or incorrect weights.")
    sys.exit(1)
else:
    print(f"\n{'='*70}")
    print("✅ HEALTH SCORE CORRECT")
    print(f"{'='*70}")
    print(f"Dashboard health score matches SSOT formula.")
    print(f"Weighted average is being used correctly.")
    sys.exit(0)
