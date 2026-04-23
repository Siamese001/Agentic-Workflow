"""Break down critical_path_integrity violations."""
import json
from collections import Counter
from pathlib import Path

artifacts = sorted(Path("artifacts/ci_gates").glob("p0_runner_full_*.json"),
                   key=lambda p: p.stat().st_mtime)
d = json.loads(artifacts[-1].read_text(encoding="utf-8"))
for r in d["results"]:
    if r["gate_family"] != "critical_path_integrity":
        continue
    by_view: Counter = Counter()
    by_layer: Counter = Counter()
    for v in r["violations"]:
        by_view[v.get("source_view") or "?"] += 1
        by_layer[v.get("layer_src") or "?"] += 1
    print(f"Total: {len(r['violations'])}")
    print("\n=== by source_view ===")
    for k, n in by_view.most_common():
        print(f"  {n:4d}  {k}")
    print("\n=== by layer_src ===")
    for k, n in by_layer.most_common():
        print(f"  {n:4d}  {k}")
    # Show spine_gap rows specifically
    print("\n=== spine_gap rows ===")
    for v in r["violations"]:
        if v.get("source_view") == "mv_runtime_spine_gaps":
            print(f"  [{v.get('layer_src','?'):10s}] {v.get('message','')}")
    break
