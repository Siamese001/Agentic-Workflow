#!/usr/bin/env python3
"""Verify which column user is seeing as 97.7%"""
import json
from pathlib import Path

project_root = Path(__file__).parent.parent

# Load dashboard data
dashboard_file = project_root / "agentic_core" / "L6_observability" / "dashboards" / "data" / "dashboard_data.js"
content = dashboard_file.read_text(encoding='utf-8')
lines = [l for l in content.split('\n') if not l.strip().startswith('//')]
content = '\n'.join(lines).replace('window.dashboardData = ', '').strip().rstrip(';')
data = json.loads(content)

total_row = next((r for r in data if r['Territory'] == 'TOTAL'), None)

print("\n" + "="*70)
print("DASHBOARD TOTAL ROW - ALL COLUMNS")
print("="*70)

if total_row:
    for key, value in total_row.items():
        marker = " ← USER SEEING THIS?" if value == 97.7 else ""
        print(f"{key:30} = {value}{marker}")
    
    print("\n" + "="*70)
    print("ANALYSIS")
    print("="*70)
    print(f"\nHealth score (correct): {total_row['Health']}")
    print(f"Code Quality Score: {total_row['Code Quality Score']}")
    
    if total_row['Code Quality Score'] == 97.7:
        print("\n⚠️  USER IS LIKELY LOOKING AT 'Code Quality Score' COLUMN")
        print("    NOT the 'Health' column!")
        print("\nThe dashboard has TWO separate scores:")
        print("  1. Health (autonomy metrics): 78.5")
        print("  2. Code Quality Score (code metrics): 97.7")
        print("\nUser needs to check they're looking at the correct column.")
else:
    print("\n❌ TOTAL row not found!")
