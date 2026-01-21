#!/usr/bin/env python3
"""
Diagnose what user is actually seeing in their browser.

User claims Table 1 Health == Table 2 Code Quality Score.
Data shows they are different (78.5 vs 97.7).

Need to check if there's a rendering bug in the HTML/JS.
"""
import json
import re
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
print("DASHBOARD DATA VERIFICATION")
print("="*70)
print(f"\nTOTAL Row in dashboard_data.js:")
print(f"  Health: {total_row['Health']}")
print(f"  Code Quality Score: {total_row['Code Quality Score']}")
print(f"  Are they the same? {total_row['Health'] == total_row['Code Quality Score']}")

# Check HTML rendering
html_file = project_root / "agentic_core" / "L6_observability" / "dashboards" / "autonomy_dashboard.html"
html_content = html_file.read_text(encoding='utf-8')

# Check if HTML has the data embedded
if 'const dashboardData = [' in html_content:
    print("\n" + "="*70)
    print("⚠️  WARNING: HTML has embedded dashboardData")
    print("="*70)
    print("The HTML file contains hardcoded data instead of loading from dashboard_data.js")
    print("This could cause the user to see stale data!")

    # Extract embedded data
    data_match = re.search(r'const dashboardData = (\[.*?\]);', html_content, re.DOTALL)
    if data_match:
        embedded_data = json.loads(data_match.group(1))
        embedded_total = next((r for r in embedded_data if r['Territory'] == 'TOTAL'), None)

        if embedded_total:
            print(f"\nEmbedded TOTAL row in HTML:")
            print(f"  Health: {embedded_total.get('Health', 'MISSING')}")
            print(f"  Code Quality Score: {embedded_total.get('Code Quality Score', 'MISSING')}")

            if embedded_total.get('Health') == embedded_total.get('Code Quality Score'):
                print("\n❌ BUG FOUND: Embedded HTML data has IDENTICAL Health and Code Quality!")
                print("This is what the user is seeing!")
            else:
                print(f"\n✅ Embedded data has different scores")
                print(f"   Health: {embedded_total.get('Health')}")
                print(f"   Code Quality Score: {embedded_total.get('Code Quality Score')}")
else:
    print("\n✅ HTML loads data from external dashboard_data.js file")

# Check if there's a JS rendering bug
print("\n" + "="*70)
print("CHECKING FOR JS RENDERING BUGS")
print("="*70)

# Look for Health column rendering
if "row['Health']" in html_content or 'row["Health"]' in html_content:
    print("✅ Found Health column rendering in JS")
else:
    print("❌ WARNING: Health column rendering not found in JS")

# Look for Code Quality Score rendering
if "row['Code Quality Score']" in html_content or 'row["Code Quality Score"]' in html_content:
    print("✅ Found Code Quality Score column rendering in JS")
else:
    print("❌ WARNING: Code Quality Score rendering not found in JS")

# Check if Health is accidentally using Code Quality value
health_render_pattern = r"row\['Health'\].*?row\['Code Quality Score'\]"
if re.search(health_render_pattern, html_content, re.DOTALL):
    print("\n⚠️  WARNING: Health and Code Quality Score references are close together")
    print("   Could indicate copy-paste error in rendering code")
