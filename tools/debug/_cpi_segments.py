"""Show the 5 mv_critical_path_segments violations."""

import json
from pathlib import Path

artifacts = sorted(Path("artifacts/ci_gates").glob("p0_runner_full_*.json"), key=lambda p: p.stat().st_mtime)
d = json.loads(artifacts[-1].read_text(encoding="utf-8"))
for r in d["results"]:
    if r["gate_family"] != "critical_path_integrity":
        continue
    for v in r["violations"]:
        if v.get("source_view") == "mv_critical_path_segments":
            print(f"  {v.get('message', '')}")
            print(f"    extra: {v.get('extra', {})}")
    print()
    print("=== top 10 mv_path_criticality_rollup ===")
    for v in r["violations"][:10]:
        if v.get("source_view") == "mv_path_criticality_rollup":
            print(f"  [{v.get('layer_src'):8s}] {v.get('message', '')[:150]}")
    break
