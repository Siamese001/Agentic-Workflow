"""Sample authority_boundary violations per breach_class / layer pair."""

import json
from pathlib import Path

artifacts = sorted(Path("artifacts/ci_gates").glob("p0_runner_full_*.json"), key=lambda p: p.stat().st_mtime)
d = json.loads(artifacts[-1].read_text(encoding="utf-8"))
seen_class = set()
seen_pair = set()
for r in d["results"]:
    if r["gate_family"] != "authority_boundary":
        continue
    for v in r["violations"]:
        extra = v.get("extra") or {}
        cls = extra.get("breach_class", "?")
        pair = f"{v.get('layer_src', '?')} -> {v.get('layer_dst', '?')}"
        key = (cls, pair)
        if key in seen_class:
            continue
        seen_class.add(key)
        print(f"=== {cls} | {pair} ===")
        print(f"  file: {v.get('file')}:{v.get('line')}")
        print(f"  msg:  {v.get('message', '')[:200]}")
        print(f"  extra: {extra}")
        print()
    break
