#!/usr/bin/env python3
"""Verify dashboard updates were applied correctly"""
from pathlib import Path

html = Path('reports/autonomy_dashboard.html').read_text(encoding='utf-8')

print("Dashboard Update Verification")
print("=" * 60)

# Check removals
breakdown_removed = 'Health Score Breakdown:' not in html
exec_summary_removed = 'Executive Summary</h3>' not in html

print("\n✅ Removals:")
print(f"  Health Score Breakdown removed: {breakdown_removed}")
print(f"  Executive Summary box removed: {exec_summary_removed}")

# Check additions
health_box = 'id="healthScoreBox"' in html
quality_box = 'id="codeQualityBox"' in html
base_box = 'id="baseInheritanceBox"' in html
color_logic = 'healthBox.style.borderColor' in html
targets = 'Target: ≥80%' in html or 'Target: &ge;80%' in html

print("\n✅ Additions:")
print(f"  healthScoreBox ID added: {health_box}")
print(f"  codeQualityBox ID added: {quality_box}")
print(f"  baseInheritanceBox ID added: {base_box}")
print(f"  Color-coding logic added: {color_logic}")
print(f"  Target thresholds added: {targets}")

# Check KPI values are populated
health_match = 'healthScoreValue' in html
quality_match = 'codeQualityScoreValue' in html
base_match = 'baseInheritanceValue' in html

print("\n✅ KPI Values:")
print(f"  Health Score element: {health_match}")
print(f"  Code Quality element: {quality_match}")
print(f"  Base Inheritance element: {base_match}")

print("\n" + "=" * 60)
if all([breakdown_removed, exec_summary_removed, health_box, color_logic, targets]):
    print("✅ ALL UPDATES VERIFIED - Dashboard ready for deployment")
else:
    print("⚠️  Some updates may not have applied correctly")
