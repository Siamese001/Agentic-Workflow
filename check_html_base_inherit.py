import json
import re

with open('agentic_core/L6_observability/dashboards/autonomy_dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Extract dashboardData
match = re.search(r'const dashboardData = (\[.*?\]);', html, re.DOTALL)
if not match:
    print("ERROR: Could not find dashboardData")
    exit(1)

data = json.loads(match.group(1))

print("=" * 80)
print("DASHBOARD HTML - BASE CLASS INHERIT % VALUES")
print("=" * 80)

# Check if field exists
first_row = data[0]
print(f"\nFirst row keys: {list(first_row.keys())}")

# Check for the field
if 'Base Class Inherit %' in first_row:
    print(f"\n✅ Field 'Base Class Inherit %' EXISTS")
    print(f"\nTOTAL row: {first_row['Territory']} = {first_row['Base Class Inherit %']}%")
    
    print(f"\nAll rows:")
    for r in data[:5]:
        print(f"  {r['Territory']}: {r.get('Base Class Inherit %', 'MISSING')}%")
else:
    print(f"\n❌ Field 'Base Class Inherit %' MISSING")
    print(f"\nLooking for similar fields:")
    for key in first_row.keys():
        if 'base' in key.lower() or 'inherit' in key.lower() or 'proper' in key.lower():
            print(f"  Found: {key} = {first_row[key]}")
