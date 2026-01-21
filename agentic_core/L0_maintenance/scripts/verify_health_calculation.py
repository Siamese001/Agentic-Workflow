#!/usr/bin/env python3
"""
Quick verification script to check health score calculation in dashboard.
"""

import json
import re
from pathlib import Path

dashboard_path = Path("reports/autonomy_dashboard.html")
if not dashboard_path.exists():
    print("❌ Dashboard not found at reports/autonomy_dashboard.html")
    exit(1)

html = dashboard_path.read_text(encoding="utf-8")

# Extract dashboardData
match = re.search(r"const dashboardData = (\[.*?\]);", html, re.DOTALL)
if not match:
    print("❌ dashboardData not found in HTML")
    exit(1)

data = json.loads(match.group(1))

# Find TOTAL row
total_row = next((r for r in data if r.get("Territory") == "TOTAL"), None)
if not total_row:
    print("❌ TOTAL row not found")
    exit(1)

# Extract components
heal_cap = float(total_row.get("Heal Cap %", 0))
invocation = float(total_row.get("Invocation %", 0))
tests = float(total_row.get("Test %", 0))
observable = float(total_row.get("Observable %", 0))
cc_health = float(total_row.get("Complexity Health", 0))
actual_health = float(total_row.get("Health", 0))

# Calculate expected
expected_health = round((heal_cap + invocation + tests + observable + cc_health) / 5, 1)

print("\n" + "=" * 80)
print("DASHBOARD HEALTH SCORE VERIFICATION")
print("=" * 80)
print("\nTOTAL Row Components:")
print(f"  Heal Capability:     {heal_cap:6.1f}%")
print(f"  Heal Invocation:     {invocation:6.1f}%")
print(f"  Test Coverage:       {tests:6.1f}%")
print(f"  Observability:       {observable:6.1f}%")
print(f"  Complexity Health:   {cc_health:6.1f}%")
print("\nHealth Score Calculation:")
print("  Formula: (Heal Cap + Invocation + Tests + Observable + CC Health) / 5")
print(f"  Expected: {expected_health:.1f}%")
print(f"  Actual:   {actual_health:.1f}%")

if abs(actual_health - expected_health) < 0.1:
    print("\n✅ PASS: Health score correctly calculated!")
else:
    print("\n❌ FAIL: Health score mismatch!")
    print(f"  Difference: {abs(actual_health - expected_health):.1f}%")

    if actual_health == 100.0:
        print("\n⚠️  WARNING: Health score is hardcoded to 100%!")
        print("  This is incorrect - it should be calculated from actual metrics.")

print("=" * 80 + "\n")

# Check a few territory rows too
print("Sample Territory Health Scores:")
print("-" * 80)
for row in data[:5]:
    if row.get("Territory") == "TOTAL":
        continue
    territory = row.get("Territory", "Unknown")
    h_cap = float(row.get("Heal Cap %", 0))
    h_inv = float(row.get("Invocation %", 0))
    t = float(row.get("Test %", 0))
    o = float(row.get("Observable %", 0))
    cc = float(row.get("Complexity Health", 0))
    h = float(row.get("Health", 0))
    exp = round((h_cap + h_inv + t + o + cc) / 5, 1)
    status = "✅" if abs(h - exp) < 0.1 else "❌"
    print(f"{status} {territory:30s} Health: {h:5.1f}% (Expected: {exp:5.1f}%)")

print("=" * 80)
