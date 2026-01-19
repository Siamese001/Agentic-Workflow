#!/usr/bin/env python3
"""Extract potential JavaScript errors from dashboard HTML."""
from pathlib import Path
import re

dashboard_path = Path("reports/autonomy_dashboard.html")
html = dashboard_path.read_text(encoding='utf-8')

print("=" * 80)
print("DASHBOARD JAVASCRIPT ERROR ANALYSIS")
print("=" * 80)

# Extract all script content
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
print(f"\nFound {len(scripts)} script blocks")

# Check for common issues
issues = []

# 1. Check for undefined variables
for i, script in enumerate(scripts, 1):
    lines = script.split('\n')
    for line_num, line in enumerate(lines, 1):
        # Look for variable usage before declaration
        if re.search(r'\b(dashboardData|recommendationsData|gaugeData|lastUpdatedStr)\b', line):
            if 'const' not in line and '=' not in line:
                issues.append(f"Script {i}, Line {line_num}: Possible use before declaration: {line.strip()[:80]}")

# 2. Check for missing function definitions
required_functions = ['loadData', 'renderGauges', 'renderRiskMatrix', 'setupDrillDowns']
for func in required_functions:
    pattern = f'function {func}'
    if pattern not in html:
        issues.append(f"Missing function definition: {func}")
    else:
        print(f"✓ Found function: {func}")

# 3. Check for DOM element references
dom_elements = re.findall(r"getElementById\(['\"]([^'\"]+)['\"]\)", html)
unique_elements = set(dom_elements)
print(f"\nDOM elements referenced: {len(unique_elements)}")

# Check if these elements exist in HTML
missing_elements = []
for elem_id in unique_elements:
    if f'id="{elem_id}"' not in html and f"id='{elem_id}'" not in html:
        missing_elements.append(elem_id)

if missing_elements:
    print(f"\n⚠️  Missing DOM elements ({len(missing_elements)}):")
    for elem in sorted(missing_elements)[:10]:
        print(f"  - {elem}")
else:
    print("\n✓ All referenced DOM elements exist")

# 4. Check for syntax errors in data injection
data_vars = ['dashboardData', 'recommendationsData', 'gaugeData', 'lastUpdatedStr']
for var in data_vars:
    pattern = f'const {var} = '
    if pattern in html:
        # Extract the value
        match = re.search(f'const {var} = (.+?);', html, re.DOTALL)
        if match:
            value = match.group(1).strip()
            if var in ['dashboardData', 'recommendationsData']:
                if value == '[]':
                    issues.append(f"{var} is empty array")
                elif not value.startswith('['):
                    issues.append(f"{var} doesn't start with array bracket")
            elif var == 'gaugeData':
                if value == '{}':
                    issues.append(f"{var} is empty object")
                elif not value.startswith('{'):
                    issues.append(f"{var} doesn't start with object brace")
        else:
            issues.append(f"Could not parse {var} value")
    else:
        issues.append(f"Missing declaration: const {var}")

# 5. Check Plotly initialization
if '__plotlyReady' in html:
    print("\n✓ Plotly loader present")
    if 'loadScript' in html:
        print("✓ loadScript function defined")
    if 'plotly.min.js' in html:
        print("✓ Local Plotly fallback configured")
    if 'cdnjs.cloudflare.com/ajax/libs/plotly' in html:
        print("✓ CDN Plotly fallback configured")
else:
    issues.append("Missing Plotly loader")

print(f"\n{'=' * 80}")
print(f"ISSUES FOUND: {len(issues)}")
print("=" * 80)

if issues:
    for issue in issues[:15]:
        print(f"  - {issue}")
    if len(issues) > 15:
        print(f"  ... and {len(issues) - 15} more")
else:
    print("✓ No critical issues detected")

print("\n" + "=" * 80)
