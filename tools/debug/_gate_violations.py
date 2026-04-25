"""Dump violations for a named gate from the latest runner artifact."""

import json
import sys
from pathlib import Path

gate = sys.argv[1] if len(sys.argv) > 1 else "critical_path_integrity"
artifacts = sorted(Path("artifacts/ci_gates").glob("p0_runner_full_*.json"), key=lambda p: p.stat().st_mtime)
d = json.loads(artifacts[-1].read_text(encoding="utf-8"))
for r in d["results"]:
    if r["gate_family"] == gate:
        print(f"=== {gate} ({len(r['violations'])} violations) ===")
        for v in r["violations"]:
            layer = v.get("layer_src") or "?"
            msg = v.get("message", "")
            extra = v.get("extra", {})
            print(f"  [{layer:10s}] {msg}")
            if extra:
                print(f"             extra: {extra}")
        break
