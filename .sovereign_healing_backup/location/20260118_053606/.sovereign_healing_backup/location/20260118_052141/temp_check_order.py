import json
from pathlib import Path
import re

html = Path('agentic_core/L6_observability/dashboards/autonomy_dashboard.html').read_text(encoding='utf-8')
m = re.search(r'const dashboardData = (\[.*?\]);', html, re.DOTALL)
data = json.loads(m.group(1))

print('Dashboard Row Order:')
print('=' * 50)
first_row = data[0].get('Territory') if data else 'NONE'
last_row = data[-1].get('Territory') if data else 'NONE'
print(f'FIRST ROW: {first_row}')
print(f'LAST ROW:  {last_row}')
print()

base_root_index = None
total_index = None
for i, r in enumerate(data):
    territory = r.get('Territory')
    if territory == 'Base/Root':
        base_root_index = i
    elif territory == 'TOTAL':
        total_index = i

print(f'Base/Root position: {base_root_index + 1 if base_root_index is not None else "NOT FOUND"}')
print(f'TOTAL position: {total_index + 1 if total_index is not None else "NOT FOUND"}')
print()

if first_row == 'Base/Root' and last_row == 'TOTAL':
    print('✅ ORDER CORRECT: Base/Root is FIRST, TOTAL is LAST')
else:
    print('❌ ORDER INCORRECT:')
    if first_row != 'Base/Root':
        print(f'   - Base/Root should be first, but {first_row} is first')
    if last_row != 'TOTAL':
        print(f'   - TOTAL should be last, but {last_row} is last')
