"""Summarize G_REACH orphan clusters from slice JSON.

Usage:
  python tools/analysis/p0_gate_slice_export.py G_REACH_l0_reachability
  python tools/analysis/p0_reach_cluster.py
  python tools/analysis/p0_reach_cluster.py artifacts/adg/p0_slices/G_REACH_l0_reachability_shadow_proof.json
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    path = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else ROOT / "artifacts/adg/p0_slices/G_REACH_l0_reachability.json"
    )
    if not path.is_absolute():
        path = ROOT / path
    data = json.loads(path.read_text(encoding="utf-8"))
    violations = data.get("violations", [])
    layers = Counter(v["extra"].get("layer", "?") for v in violations)
    prefixes = Counter()
    for v in violations:
        parts = v["subject"].split("/")
        prefixes["/".join(parts[:3]) if len(parts) >= 3 else v["subject"]] += 1
    print(f"source={path.relative_to(ROOT).as_posix()} count={data.get('count', len(violations))}")
    print("by_layer:", dict(layers.most_common()))
    print("top_prefixes:")
    for pref, n in prefixes.most_common(20):
        print(f"  {n:4d} {pref}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
