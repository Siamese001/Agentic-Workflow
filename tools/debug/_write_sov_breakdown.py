"""Break down write_sovereignty violations."""

import json
from collections import Counter
from pathlib import Path

artifacts = sorted(Path("artifacts/ci_gates").glob("p0_runner_full_*.json"), key=lambda p: p.stat().st_mtime)
d = json.loads(artifacts[-1].read_text(encoding="utf-8"))
for r in d["results"]:
    if r["gate_family"] != "write_sovereignty":
        continue
    by_view: Counter = Counter()
    by_layer: Counter = Counter()
    by_severity: Counter = Counter()
    by_kind: Counter = Counter()
    by_prefix: Counter = Counter()
    for v in r["violations"]:
        by_view[v.get("source_view") or "?"] += 1
        by_layer[v.get("layer_src") or "?"] += 1
        extra = v.get("extra") or {}
        by_severity[extra.get("severity", "?")] += 1
        # Try common kind fields
        k = (
            extra.get("violation_kind")
            or extra.get("gap_type")
            or extra.get("breach_class")
            or extra.get("reason")
            or "?"
        )
        by_kind[k] += 1
        f = v.get("file") or "?"
        by_prefix["/".join(f.split("/")[:3])] += 1
    print(f"Total: {len(r['violations'])}")
    print("\n=== by source_view ===")
    for k, n in by_view.most_common():
        print(f"  {n:5d}  {k}")
    print("\n=== by layer_src ===")
    for k, n in by_layer.most_common():
        print(f"  {n:5d}  {k}")
    print("\n=== by extra.severity ===")
    for k, n in by_severity.most_common():
        print(f"  {n:5d}  {k}")
    print("\n=== by kind/gap_type/breach_class ===")
    for k, n in by_kind.most_common():
        print(f"  {n:5d}  {k}")
    print("\n=== top path prefixes ===")
    for k, n in by_prefix.most_common(15):
        print(f"  {n:5d}  {k}")
    print("\n=== 2 samples per source_view ===")
    seen: Counter = Counter()
    for v in r["violations"]:
        sv = v.get("source_view") or "?"
        if seen[sv] >= 2:
            continue
        seen[sv] += 1
        print(f"  [{sv}] {v.get('file')}")
        print(f"     msg: {v.get('message', '')[:200]}")
        print(f"     extra: {v.get('extra', {})}")
    break
