#!/usr/bin/env python3
"""Check if Health and Code Quality Score are identical across all rows."""
import json
from pathlib import Path

project_root = Path(__file__).parent.parent

# Load dashboard data
dashboard_file = project_root / "agentic_core" / "L6_observability" / "dashboards" / "data" / "dashboard_data.js"
content = dashboard_file.read_text(encoding='utf-8')
lines = [l for l in content.split('\n') if not l.strip().startswith('//')]
content = '\n'.join(lines).replace('window.dashboardData = ', '').strip().rstrip(';')
data = json.loads(content)

print("\n" + "="*70)
print("CHECKING ALL ROWS: Health vs Code Quality Score")
print("="*70)

identical_count = 0
different_count = 0

for row in data:
    territory = row.get('Territory', 'UNKNOWN')
    health = row.get('Health', None)
    code_quality = row.get('Code Quality Score', None)
    
    if health is not None and code_quality is not None:
        is_same = abs(health - code_quality) < 0.01
        
        if is_same:
            identical_count += 1
            print(f"❌ IDENTICAL: {territory:30} Health={health:6.1f} CodeQuality={code_quality:6.1f}")
        else:
            different_count += 1
            if different_count <= 5:  # Show first 5 different ones
                print(f"✅ DIFFERENT: {territory:30} Health={health:6.1f} CodeQuality={code_quality:6.1f}")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"Rows with IDENTICAL scores: {identical_count}")
print(f"Rows with DIFFERENT scores: {different_count}")

if identical_count > 0:
    print("\n❌ BUG CONFIRMED: Health and Code Quality Score are IDENTICAL in some rows!")
    print("This means health score calculation is using wrong formula.")
else:
    print("\n✅ All rows have different Health and Code Quality scores (correct)")
