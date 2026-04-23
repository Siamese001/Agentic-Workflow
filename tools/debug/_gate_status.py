"""Print latest p0 runner gate status summary."""
import json
from pathlib import Path

artifacts = sorted(Path("artifacts/ci_gates").glob("p0_runner_full_*.json"),
                   key=lambda p: p.stat().st_mtime)
latest = artifacts[-1]
print(f"Source: {latest.name}\n")
d = json.loads(latest.read_text(encoding="utf-8"))
for r in d["results"]:
    print(f"  {r['gate_family']:28s} {r['status']:8s} {len(r.get('violations', []))}")
