"""List (src_file, dst_file) pairs for all mv_authority_boundary_breaches."""

import json
from collections import Counter
from pathlib import Path

artifacts = sorted(Path("artifacts/ci_gates").glob("p0_runner_full_*.json"), key=lambda p: p.stat().st_mtime)
d = json.loads(artifacts[-1].read_text(encoding="utf-8"))
pairs: Counter = Counter()
for r in d["results"]:
    if r["gate_family"] != "authority_boundary":
        continue
    for v in r["violations"]:
        extra = v.get("extra") or {}
        cls = extra.get("breach_class")
        if cls not in ("L6_downstream_mutation", "L_APP_core_bypass"):
            continue
        src = v.get("file") or "?"
        dst = extra.get("dst_file", "?")
        pairs[(src, dst)] += 1
print(f"Total structural breach edges: {sum(pairs.values())}")
print(f"Distinct (src,dst) pairs: {len(pairs)}\n")
print("=== top 30 (src, dst) by count ===")
for (src, dst), n in pairs.most_common(30):
    print(f"  {n:3d}  {src}  ->  {dst}")

print("\n=== dst files ranked ===")
dsts: Counter = Counter()
for (src, dst), n in pairs.items():
    dsts[dst] += n
for dst, n in dsts.most_common(15):
    print(f"  {n:3d}  {dst}")
