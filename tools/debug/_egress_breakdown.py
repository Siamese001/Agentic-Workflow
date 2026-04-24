"""Break down capability_egress violations."""
import json
from collections import Counter
from pathlib import Path

artifacts = sorted(Path("artifacts/ci_gates").glob("p0_runner_full_*.json"),
                   key=lambda p: p.stat().st_mtime)
d = json.loads(artifacts[-1].read_text(encoding="utf-8"))
for r in d["results"]:
    if r["gate_family"] != "capability_egress":
        continue
    by_view: Counter = Counter()
    by_layer: Counter = Counter()
    by_gap_type: Counter = Counter()
    by_file_prefix: Counter = Counter()
    for v in r["violations"]:
        by_view[v.get("source_view") or "?"] += 1
        by_layer[v.get("layer_src") or "?"] += 1
        extra = v.get("extra") or {}
        by_gap_type[extra.get("gap_type", "?")] += 1
        f = v.get("file") or "?"
        prefix = "/".join(f.split("/")[:3])
        by_file_prefix[prefix] += 1
    print(f"Total: {len(r['violations'])}")
    print("\n=== by source_view ===")
    for k, n in by_view.most_common():
        print(f"  {n:4d}  {k}")
    print("\n=== by layer_src ===")
    for k, n in by_layer.most_common():
        print(f"  {n:4d}  {k}")
    print("\n=== by gap_type ===")
    for k, n in by_gap_type.most_common():
        print(f"  {n:4d}  {k}")
    print("\n=== by top-3 path prefix ===")
    for k, n in by_file_prefix.most_common(15):
        print(f"  {n:4d}  {k}")
    print("\n=== 3 sample violations per gap_type ===")
    seen: Counter = Counter()
    for v in r["violations"]:
        extra = v.get("extra") or {}
        gt = extra.get("gap_type", "?")
        if seen[gt] >= 2:
            continue
        seen[gt] += 1
        print(f"  [{gt}] {v.get('file')}")
        print(f"     msg: {v.get('message','')[:180]}")
        print(f"     extra: {extra}")
    break
