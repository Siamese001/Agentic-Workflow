import re
from collections import Counter

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "count_territories_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "count_territories_util", "p0_governance")
_emit_snapshots_state("p0", "count_territories_util", "state_snapshot")

pat = re.compile('"Territory":\\s*"([^"]+)",\\s*"Total":\\s*(\\d+)')
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
