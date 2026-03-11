import re
from collections import Counter

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pat = re.compile(r'"Territory":\s*"([^"]+)",\s*"Total":\s*(\d+)')

counts = Counter()

with open("agentic_core/L6_observability/dashboards/autonomy_dashboard.html", encoding="utf-8") as f:
    for line in f:
        for m in pat.finditer(line):
            territory = m.group(1)
            count = int(m.group(2))
            counts[territory] += count

print("Territory Agent Counts:")
print("=" * 60)
for territory, cnt in counts.most_common(35):
    print(f"{territory:45} {cnt:>4}")
