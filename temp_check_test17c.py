import json
from pathlib import Path
import re

html = Path('agentic_core/L6_observability/dashboards/autonomy_dashboard.html').read_text(encoding='utf-8')
match = re.search(r'const dashboardData = (\[.*?\]);', html, re.DOTALL)
data = json.loads(match.group(1))

print("Checking Test 17C - Dashboard row validation")
print("=" * 70)

invalid_rows = []
for row in data:
    territory = row.get('Territory', 'UNKNOWN')
    if territory == 'TOTAL':
        continue
    
    total = row.get('Total', 0)
    if total == 0:
        invalid_rows.append(f"{territory}: Total=0 (empty territory)")
    
    # Check critical fields have valid values
    for field in ['Heal Cap %', 'Test %', 'Observable %', 'Health']:
        val = row.get(field)
        if val is None:
            invalid_rows.append(f"{territory}: {field}=None")
        elif val != 'N/A' and not isinstance(val, (int, float)):
            invalid_rows.append(f"{territory}: {field}={val} (not numeric or N/A)")

if invalid_rows:
    print(f"Found {len(invalid_rows)} invalid rows:")
    for inv in invalid_rows[:10]:
        print(f"  - {inv}")
else:
    print("All rows valid!")
