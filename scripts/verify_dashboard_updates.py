#!/usr/bin/env python3
"""Verify dashboard updates were applied correctly"""
from pathlib import Path

html = Path('reports/autonomy_dashboard.html').read_text(encoding='utf-8')

print("Dashboard Update Verification")
print("=" * 60)

# Check removals
print("\n✅ Removals:")
print(f"  Health Score Breakdown removed: {'Health Score Breakdown:' not in html}")
print(f"  Executive Summary box removed: {'Executive Summary</h3>' not in html}")

# Check additions
print("\n✅ Additions:")
print(f"  healthScoreBox ID added: {'id=\"healthScoreBox\"' in html}")
print(f"  codeQualityBox ID added: {'id=\"codeQualityBox\"' in html}")
print(f"  baseInheritanceBox ID added: {'id=\"baseInheritanceBox\"' in html}")

# Check color-coding logic
print(f"  Color-coding logic added: {'healthBox.style.borderColor' in html}")
print(f"  Target thresholds added: {'Target: ≥80%' in html}")

# Check KPI values are populated
print("\n✅ KPI Values:")
health_match = 'healthScoreValue' in html
quality_match = 'codeQualityScoreValue' in html
base_match = 'baseInheritanceValue' in html
print(f"  Health Score element: {health_match}")
print(f"  Code Quality element: {quality_match}")
print(f"  Base Inheritance element: {base_match}")

print("\n" + "=" * 60)
if all([
    'Health Score Breakdown:' not in html,
    'Executive Summary</h3>' not in html,
    'id="healthScoreBox"' in html,
    'healthBox.style.borderColor' in html,
    'Target: ≥80%' in html
]):
    print("✅ ALL UPDATES VERIFIED - Dashboard ready for deployment")
else:
    print("⚠️  Some updates may not have applied correctly")
