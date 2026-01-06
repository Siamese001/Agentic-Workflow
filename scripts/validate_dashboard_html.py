#!/usr/bin/env python3
"""Validate dashboard HTML for loading issues."""
from pathlib import Path
import re

dashboard_path = Path("reports/autonomy_dashboard.html")
html = dashboard_path.read_text(encoding='utf-8')

print("=" * 80)
print("DASHBOARD HTML VALIDATION")
print("=" * 80)

# Check basic structure
print(f"\nFile size: {len(html):,} bytes")
print(f"Has <!DOCTYPE html>: {'<!DOCTYPE html>' in html}")
print(f"Has <html>: {'<html' in html}")
print(f"Has <head>: {'<head>' in html}")
print(f"Has <body>: {'<body>' in html}")

# Check for data injection
print(f"\nHas 'const dashboardData': {'const dashboardData' in html}")
print(f"Has 'const recommendationsData': {'const recommendationsData' in html}")
print(f"Has 'const lastUpdatedStr': {'const lastUpdatedStr' in html}")
print(f"Has 'const gaugeData': {'const gaugeData' in html}")

# Check for Plotly
print(f"\nHas Plotly loader: {'__plotlyReady' in html}")
print(f"Has Plotly reference: {'window.Plotly' in html}")

# Check for JavaScript errors
lines = html.split('\n')
syntax_issues = []
for i, line in enumerate(lines, 1):
    # Check for common JS syntax errors
    if 'undefined' in line and 'typeof' not in line:
        syntax_issues.append(f"Line {i}: possible undefined reference")
    if line.strip().startswith('const') and '=' not in line:
        syntax_issues.append(f"Line {i}: incomplete const declaration")

print(f"\nPotential syntax issues: {len(syntax_issues)}")
if syntax_issues:
    for issue in syntax_issues[:5]:
        print(f"  {issue}")

# Check for script tags
script_count = html.count('<script')
print(f"\nScript tags: {script_count}")

# Check for closing tags
print(f"Closing </html>: {'</html>' in html}")
print(f"Closing </body>: {'</body>' in html}")
print(f"Closing </head>: {'</head>' in html}")

# Look for the main initialization
print(f"\nHas DOMContentLoaded: {'DOMContentLoaded' in html}")
print(f"Has renderDashboard function: {'function renderDashboard' in html or 'renderDashboard(' in html}")

# Check if dashboardData is actually populated
if 'const dashboardData' in html:
    match = re.search(r'const dashboardData = (\[.*?\]);', html, re.DOTALL)
    if match:
        data_str = match.group(1)
        if data_str == '[]':
            print("\n⚠️  WARNING: dashboardData is empty array!")
        else:
            # Count territories
            territory_count = data_str.count('"Territory"')
            print(f"\n✓ dashboardData populated with ~{territory_count} territories")
    else:
        print("\n⚠️  WARNING: Could not parse dashboardData!")

print("\n" + "=" * 80)
