"""Check recent DEFERRED_SCOPE hook log entries for current session markers."""

import json
from pathlib import Path

p = Path("artifacts/cursor/deferred_scope_capture.jsonl")
recent = []
for line in p.read_text(encoding="utf-8").splitlines():
    try:
        j = json.loads(line)
        if j.get("timestamp", "") >= "2026-04-24T08":
            recent.append(j)
    except (json.JSONDecodeError, KeyError):
        pass
print(f"Entries since 2026-04-24T08:00Z: {len(recent)}")
for j in recent:
    m = j.get("marker", {})
    ts = j.get("timestamp", "?")[:19]
    plan = m.get("plan", "?")
    phase = m.get("phase", "?")
    kind = j.get("kind", "?")
    band = j.get("band", "?")
    print(f"  {ts}  plan={plan}  phase={phase}  kind={kind}  band={band}")
