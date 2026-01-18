#!/usr/bin/env python3
"""Check what's actually rendering in the dashboard."""
from pathlib import Path
import re

dashboard_path = Path("reports/autonomy_dashboard.html")
html = dashboard_path.read_text(encoding='utf-8')

print("=" * 80)
print("DASHBOARD RENDERING CHECK")
print("=" * 80)

# Check what functions are called in loadData()
loaddata_match = re.search(r'function loadData\(\).*?(?=function\s+\w+\(|$)', html, re.DOTALL)
if loaddata_match:
    loaddata_code = loaddata_match.group(0)
    
    print("\nFunctions called in loadData():")
    render_calls = re.findall(r'(render\w+)\(', loaddata_code)
    for call in render_calls:
        print(f"  - {call}()")
    
    print("\nExpected sections:")
    print("  ✓ KPIs (2 big boxes: Health Score, Code Quality Score)")
    print("  ✓ Strategic Recommendations")
    print("  ✓ Territory Breakdown Table (kpiGrid)")
    print("  ✓ Gauge Charts (healthGauge, complianceGauge)")
    print("  ✓ Risk Matrix (bubble chart)")
    print("  ✓ Territory Charts (health, healing, compliance, observability, complexity)")
    print("  ✓ Base Agent Inheritance Chart (by L0-L5)")

# Check if renderTerritorySummaryTable exists and what it does
territory_table_match = re.search(r'function renderTerritorySummaryTable\(.*?\n\s*\}', html, re.DOTALL)
if territory_table_match:
    print("\n✓ renderTerritorySummaryTable() function exists")
    # Check if it creates a table
    if '<table' in territory_table_match.group(0):
        print("  ✓ Creates HTML table")
    if 'kpiGrid' in territory_table_match.group(0):
        print("  ✓ Renders into #kpiGrid container")

# Check if renderBaseInheritanceChart exists
base_inheritance_match = re.search(r'function renderBaseInheritanceChart\(.*?\n\s*\}', html, re.DOTALL)
if base_inheritance_match:
    print("\n✓ renderBaseInheritanceChart() function exists")
    if '<table' in base_inheritance_match.group(0):
        print("  ✓ Creates HTML table")
    if 'baseInheritanceTable' in base_inheritance_match.group(0):
        print("  ✓ Renders into #baseInheritanceTable container")

# Check the actual structure in the HTML
print("\n" + "=" * 80)
print("DASHBOARD STRUCTURE")
print("=" * 80)

sections = [
    ("Health Score KPI", 'id="healthScoreBox"'),
    ("Code Quality KPI", 'id="codeQualityBox"'),
    ("Strategic Recommendations", 'Strategic Recommendations'),
    ("Territory Table Container", 'id="kpiGrid"'),
    ("Health Gauge", 'id="healthGauge"'),
    ("Compliance Gauge", 'id="complianceGauge"'),
    ("Risk Matrix", 'id="riskMatrix"'),
    ("Health Chart", 'id="healthChart"'),
    ("Healing Chart", 'id="healingChart"'),
    ("Compliance Chart", 'id="complianceChart"'),
    ("Observability Chart", 'id="observabilityChart"'),
    ("Complexity Chart", 'id="complexityChart"'),
    ("Base Inheritance Table", 'id="baseInheritanceTable"'),
]

for name, pattern in sections:
    exists = pattern in html
    print(f"  {'✓' if exists else '✗'} {name}")

print("\n" + "=" * 80)
