"""Show all 27 mv_gateway_bypass_paths violations."""
import json
from collections import Counter
from pathlib import Path
artifacts = sorted(Path("artifacts/ci_gates").glob("p0_runner_full_*.json"),
                   key=lambda p: p.stat().st_mtime)
d = json.loads(artifacts[-1].read_text(encoding="utf-8"))
for r in d["results"]:
    if r["gate_family"] != "capability_egress":
        continue
    by_file: Counter = Counter()
    by_symbol: Counter = Counter()
    print("=== all gateway_bypass violations ===")
    for v in r["violations"]:
        if v.get("source_view") != "mv_gateway_bypass_paths":
            continue
        extra = v.get("extra") or {}
        sym = extra.get("provider_symbol", "?")
        by_file[v.get("file","?")] += 1
        by_symbol[sym] += 1
        print(f"  {v.get('file')}  ::  {sym}  ({extra.get('bypass_type')})")
    print("\n=== by file ===")
    for k, n in by_file.most_common(): print(f"  {n:3d}  {k}")
    print("\n=== by symbol ===")
    for k, n in by_symbol.most_common(): print(f"  {n:3d}  {k}")
    print("\n=== 20 provider_without_capability_route files ===")
    for v in r["violations"]:
        extra = v.get("extra") or {}
        if extra.get("gap_type") != "provider_without_capability_route":
            continue
        print(f"  inv={extra.get('provider_invoke_count')}  {v.get('file')}")
    break
