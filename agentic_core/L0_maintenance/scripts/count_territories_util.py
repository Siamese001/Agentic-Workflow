import re
from collections import Counter

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
