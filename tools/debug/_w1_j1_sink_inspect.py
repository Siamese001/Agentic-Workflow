"""Inspect the wiring-gate JSONL sink after a run."""

import json
from collections import Counter
from pathlib import Path

p = Path("artifacts/governance/wiring_gate_violations.jsonl")
lines = p.read_text(encoding="utf-8").strip().splitlines()
print(f"total_runs_logged: {len(lines)}")

last = json.loads(lines[-1])
print(f"last_run:")
print(f"  gate_id  : {last['gate_id']}")
print(f"  tier     : {last['tier']}")
print(f"  status   : {last['status']}")
print(f"  snapshot : {last['snapshot']}")
print(f"  timestamp: {last['timestamp']}")
print(f"rule breakdown:")
for rule, count in Counter(v["rule"] for v in last["violations"]).most_common():
    print(f"  {rule:35s} {count}")
print(f"severity breakdown:")
for sev, count in Counter(v["severity"] for v in last["violations"]).most_common():
    print(f"  {sev:35s} {count}")
