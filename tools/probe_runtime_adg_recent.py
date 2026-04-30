"""Probe the runtime ADG store for spans/edges from the latest apps_rg run.

Discovers files modified in the last 30 minutes under
`agentic_core/L4_state/memory/runtime_adg/`, samples the freshest versioned
snapshot, and prints a structural summary of what landed: span count,
edge_kind distribution, layer distribution, lifecycle traces present.
"""
from __future__ import annotations

import json
import pathlib
import time

BASE = pathlib.Path("agentic_core/L4_state/memory/runtime_adg")
CUTOFF = time.time() - 30 * 60


def main() -> int:
    recent: list[tuple[float, pathlib.Path]] = []
    for d in BASE.iterdir():
        if d.is_dir() and len(d.name) == 2:
            for f in d.rglob("*"):
                if f.is_file() and f.stat().st_mtime > CUTOFF:
                    recent.append((f.stat().st_mtime, f))
    recent.sort()
    print(f"recent_files_30min={len(recent)}")
    for mt, f in recent[-10:]:
        ts = time.strftime("%H:%M:%S", time.localtime(mt))
        print(f"  {ts} {f.relative_to(BASE)} {f.stat().st_size}b")

    if not recent:
        print("[probe] no recent files; runtime ADG was not updated by latest run")
        return 1

    # Sample the freshest JSON file
    json_files = [f for _, f in recent if f.suffix == ".json"]
    if not json_files:
        print("[probe] no JSON snapshot files found in recent set")
        return 0

    freshest = json_files[-1]
    print()
    print(f"[probe] freshest_snapshot={freshest.relative_to(BASE)}")
    try:
        snap = json.loads(freshest.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"[probe] failed to parse: {exc}")
        return 1

    print(f"  top_level_keys={list(snap.keys())[:20]}")
    if "spans" in snap:
        spans = snap["spans"]
        print(f"  spans_count={len(spans)}")
        if spans:
            sample = spans[0]
            print(f"  sample_span_keys={list(sample.keys())[:15]}")
            # Edge-kind distribution
            ek_counts: dict[str, int] = {}
            layer_counts: dict[str, int] = {}
            for s in spans:
                attrs = s.get("attributes", {}) if isinstance(s, dict) else {}
                ek = attrs.get("edge_kind") or s.get("edge_kind") or "(none)"
                ek_counts[ek] = ek_counts.get(ek, 0) + 1
                lyr = attrs.get("layer") or s.get("layer") or "(none)"
                layer_counts[lyr] = layer_counts.get(lyr, 0) + 1
            print(f"  edge_kinds_top10={sorted(ek_counts.items(), key=lambda x: -x[1])[:10]}")
            print(f"  layers={sorted(layer_counts.items(), key=lambda x: -x[1])}")
    if "edges" in snap:
        print(f"  edges_count={len(snap['edges'])}")
    if "trace_id" in snap:
        print(f"  trace_id={snap['trace_id']}")
    if "mission" in snap:
        print(f"  mission={snap['mission']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
