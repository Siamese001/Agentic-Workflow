import json
import re

# Read dashboard HTML
with open('agentic_core/L6_observability/dashboards/autonomy_dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Extract dashboardData
match = re.search(r'const dashboardData = (\[.*?\]);', html, re.DOTALL)
if not match:
    print("ERROR: Could not find dashboardData in HTML")
    exit(1)

data = json.loads(match.group(1))

print("=" * 80)
print("DASHBOARD PROPER BASE % VALUES")
print("=" * 80)

# Check TOTAL row
total_row = [r for r in data if r['Territory'] == 'TOTAL'][0]
print(f"\nTOTAL row: Proper Base % = {total_row['Proper Base %']}%")

# Check Base Class territories
base_territories = [r for r in data if 'Base Class' in r['Territory']]
print(f"\nBase Class territories ({len(base_territories)}):")
for r in base_territories:
    print(f"  {r['Territory']}: {r['Proper Base %']}%")

# Check a few other territories
print(f"\nSample other territories:")
other = [r for r in data if r['Territory'] not in ['TOTAL'] and 'Base Class' not in r['Territory']]
for r in other[:5]:
    print(f"  {r['Territory']}: {r['Proper Base %']}%")
