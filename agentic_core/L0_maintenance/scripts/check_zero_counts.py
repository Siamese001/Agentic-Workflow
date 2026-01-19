"""Check for any 0-count territory rows in dashboard."""
import json
import re
from archives.location_violations.file_utils import safe_read_file, safe_write_file

html = open('agentic_core/L6_observability/dashboards/autonomy_dashboard.html', encoding='utf-8').read()

# Extract dashboardData
lines = []
in_data = False
for line in html.split('\n'):
    if 'const dashboardData = [' in line:
        in_data = True
        lines.append('[')
        continue
    if in_data:
        lines.append(line)
        if '];' in line:
            lines[-1] = lines[-1].replace('];', ']')
            break

data = json.loads(''.join(lines))

print("=" * 70)
print("ZERO-COUNT CHECK")
print("=" * 70)
print(f"\nTotal rows: {len(data)}")
print()

zero_count = [r for r in data if r.get('Total', 0) == 0 and r['Territory'] != 'TOTAL']
if zero_count:
    print(f"❌ FOUND {len(zero_count)} territories with 0 agents:")
    for r in zero_count:
        print(f"   - {r['Territory']}")
else:
    print("✅ NO territories with 0 agents (empty placeholders removed)")

print()
print("All territories in dashboard:")
for r in data:
    print(f"  {r['Territory']}: {r['Total']} agents")
