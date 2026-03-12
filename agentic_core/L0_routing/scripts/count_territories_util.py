import re
from collections import Counter
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
pat = re.compile('"Territory":\\s*"([^"]+)",\\s*"Total":\\s*(\\d+)')
counts = Counter()
with open('agentic_core/L6_observability/dashboards/autonomy_dashboard.html', encoding='utf-8') as f:
    for line in f:
        for m in pat.finditer(line):
            territory = m.group(1)
            count = int(m.group(2))
            counts[territory] += count
print('Territory Agent Counts:')
print('=' * 60)
for territory, cnt in counts.most_common(35):
    print(f'{territory:45} {cnt:>4}')
