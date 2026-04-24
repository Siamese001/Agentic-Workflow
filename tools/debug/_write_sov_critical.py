"""Show the 93 critical write_sovereignty violations."""
import json
from collections import Counter
from pathlib import Path

artifacts = sorted(Path("artifacts/ci_gates").glob("p0_runner_full_*.json"),
                   key=lambda p: p.stat().st_mtime)
d = json.loads(artifacts[-1].read_text(encoding="utf-8"))
for r in d["results"]:
    if r["gate_family"] != "write_sovereignty":
        continue
    by_file: Counter = Counter()
    by_symbol: Counter = Counter()
    by_layer: Counter = Counter()
    for v in r["violations"]:
        extra = v.get("extra") or {}
        if extra.get("severity") != "critical":
            continue
        by_file[v.get("file") or "?"] += 1
        by_symbol[extra.get("write_symbol") or "?"] += 1
        by_layer[v.get("layer_src") or "?"] += 1
    print(f"Critical total: {sum(by_file.values())}")
    print("\n=== by layer ===")
    for k, n in by_layer.most_common(): print(f"  {n:4d}  {k}")
    print("\n=== top 20 files ===")
    for k, n in by_file.most_common(20): print(f"  {n:4d}  {k}")
    print("\n=== top 15 write symbols ===")
    for k, n in by_symbol.most_common(15): print(f"  {n:4d}  {k}")
    break
