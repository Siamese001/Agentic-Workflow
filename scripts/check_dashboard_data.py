"""Check dashboard data for TOTAL row values."""
import json
import re

with open('reports/autonomy_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the dashboardData using regex
match = re.search(r'const dashboardData = (\[.*?\]);', content, re.DOTALL)
if match:
    data_str = match.group(1)
    data = json.loads(data_str)
    
    # Find TOTAL row
    total = next((r for r in data if r.get('Territory') == 'TOTAL'), None)
    if total:
        print('=== TOTAL Row Values in Dashboard ===')
        print(f"  Typed %: {total.get('Typed %')}")
        print(f"  Documented %: {total.get('Documented %')}")
        print(f"  Observable %: {total.get('Observable %')}")
        print(f"  Schema Strictness %: {total.get('Schema Strictness %', 'N/A')}")
        print(f"  Health: {total.get('Health')}")
        print(f"  Code Quality Score: {total.get('Code Quality Score')}")
        print(f"  Heal Invocation %: {total.get('Heal Invocation %')}")
        print(f"  Hardened %: {total.get('Hardened %')}")
        print(f"  Test %: {total.get('Test %')}")
        print(f"  Metadata %: {total.get('Metadata %')}")
        print(f"  Complexity Health: {total.get('Complexity Health')}")
    else:
        print('TOTAL row not found in dashboard data')
        print('Available territories:', [r.get('Territory') for r in data[:5]])
else:
    print('Could not find dashboardData in HTML')
