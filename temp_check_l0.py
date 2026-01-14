import json
from pathlib import Path
import re

html = Path('agentic_core/L6_observability/dashboards/autonomy_dashboard.html').read_text(encoding='utf-8')
match = re.search(r'const dashboardData = (\[.*?\]);', html, re.DOTALL)
data = json.loads(match.group(1))

l0_rows = [r for r in data if 'L0' in r.get('Territory', '')]

print('L0 Maintenance Territories:')
print('=' * 70)
for row in l0_rows:
    print(f"Territory: {row['Territory']}")
    print(f"  Heal Cap %: {row.get('Heal Cap %', 'N/A')}")
    print(f"  Invocation %: {row.get('Invocation %', 0)}")
    print(f"  Health: {row.get('Health', 0)}")
    print()
