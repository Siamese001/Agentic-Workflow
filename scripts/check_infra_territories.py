#!/usr/bin/env python3
"""Check infrastructure territories in generated dashboard."""
import json
import re
from pathlib import Path

dashboard = Path('reports/autonomy_dashboard.html').read_text(encoding='utf-8')

# Find dashboardData JSON
match = re.search(r'const dashboardData = (\[.*?\]);', dashboard, re.DOTALL)
if match:
    data = json.loads(match.group(1))
    total_row = next((r for r in data if r.get('Territory') == 'TOTAL'), None)
    if total_row:
        print(f"TOTAL agents: {total_row.get('Total')}")
        print(f"Infrastructure Total: {total_row.get('Infrastructure Total')}")
        print(f"Infrastructure Territories: {total_row.get('Infrastructure Territories')}")
    
    # Check for observability row
    print("\nAll territories:")
    for row in data:
        terr = row.get('Territory', '')
        total = row.get('Total', 0)
        is_infra = row.get('IsInfrastructure', False)
        if terr != 'TOTAL':
            infra_label = " [INFRA]" if is_infra else ""
            print(f"  {terr}: {total} agents{infra_label}")
else:
    print("Could not find dashboardData in HTML")
