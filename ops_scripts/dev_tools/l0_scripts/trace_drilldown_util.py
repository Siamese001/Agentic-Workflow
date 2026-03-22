"""Trace what territory names are used in onclick handlers"""
import re
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)

html = Path('reports/autonomy_dashboard.html').read_text(encoding='utf-8')
pattern = 'onclick=\\"openDrillModal\\(\'([^\']+)\'(?:,\\s*\'([^\']*)\')?\\)\\"'
matches = re.findall(pattern, html)
print('Drill-down onclick handlers found:')
print('=' * 70)
territories_clicked = set()
for territory, sub in matches[:30]:
    territories_clicked.add(territory)
    print(f"  Territory: '{territory}' | Sub: '{sub}'")
print('\n' + '=' * 70)
print(f'Unique territories in onclick: {len(territories_clicked)}')
import json

from agentic_core.runtime.lifecycle_trace_contract import (
    emit_determinism_digest,
    record_execution_trace,
)

emit_determinism_digest("trace_drilldown_util", "trace_drilldown_util_digest")
record_execution_trace("trace_drilldown_util", "trace_drilldown_util_trace")

data_start = html.find('const dashboardData = ')
data_end = html.find('];', data_start)
data_str = html[data_start + 22:data_end + 1]
dashboard_data = json.loads(data_str)
data_territories = {r.get('Territory') for r in dashboard_data if r.get('Territory') != 'TOTAL'}
print(f'Territories in dashboardData: {len(data_territories)}')
onclick_only = territories_clicked - data_territories
data_only = data_territories - territories_clicked
if onclick_only:
    print('\n❌ In onclick but NOT in dashboardData:')
    for t in onclick_only:
        print(f"   '{t}'")
if data_only:
    print('\n⚠️  In dashboardData but NOT in onclick:')
    for t in data_only:
        print(f"   '{t}'")
if not onclick_only and (not data_only):
    print('\n✅ All territory names match!')
