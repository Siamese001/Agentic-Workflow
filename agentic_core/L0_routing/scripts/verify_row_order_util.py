"""Verify dashboard row order"""
import json
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
with open('agentic_core/L6_observability/dashboards/data/dashboard_data.js', encoding='utf-8') as f:
    content = f.read()
    start = content.find('[')
    end = content.rfind(']') + 1
    data = json.loads(content[start:end])
print('Dashboard Row Order:')
print('=' * 70)
for i, row in enumerate(data, 1):
    territory = row['Territory']
    print(f'{i:2}. {territory}')
print('=' * 70)
print(f"\n✅ First row: {data[0]['Territory']}")
print(f"✅ Last row: {data[-1]['Territory']}")
print(f'✅ Total rows: {len(data)}')
expected_first = 'Sovereign Base Agent'
expected_last = 'TOTAL'
if data[0]['Territory'] == expected_first and data[-1]['Territory'] == expected_last:
    print('\n✅ Row order is CORRECT!')
else:
    print('\n❌ Row order is WRONG!')
    print(f"   Expected first: {expected_first}, got: {data[0]['Territory']}")
    print(f"   Expected last: {expected_last}, got: {data[-1]['Territory']}")
