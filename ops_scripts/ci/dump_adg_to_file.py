"""
Dump a detailed AST dependency graph for all sovereign territory folders to
artifacts/adg/adg_full_<timestamp>.json for future analysis.

Output sections
---------------
- meta          : build timestamp, scan roots, SSOT version
- stats         : node/edge counts, orphans, cycles, violations
- nodes         : every module with file path, layer, in-degree, out-degree
- edges         : every directed import edge (src -> dst)
- adjacency     : per-module direct imports + direct importers (1-hop)
- orphans       : modules with no connections inside the repo
- cycles        : all import cycles detected
- layer_violations : (src, dst, src_layer, dst_layer) gravity inversions
- fan_in_top50  : 50 most-imported (highest fan-in) modules
- fan_out_top50 : 50 modules with most imports (highest fan-out)
- syntax_errors : files that failed AST parsing
- module_to_file: full module-name -> relative-file-path mapping

Usage
-----
    python ops_scripts/ci/dump_adg_to_file.py            # use cached graph
    python ops_scripts/ci/dump_adg_to_file.py --rebuild  # force full re-parse
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.dep_graph_db import SSOT_DIRS, build  # noqa: E402

OUT_DIR = ROOT / "artifacts" / "adg"


def _dump(force_rebuild: bool) -> Path:
    print(f"[ADG] Building dependency graph (force_rebuild={force_rebuild})…")
    dg = build(force=force_rebuild)

    print("[ADG] Collecting stats…")
    stats = dg.stats()

    print("[ADG] Collecting nodes…")
    nodes = {}
    for node, data in sorted(dg._g.nodes(data=True)):
        nodes[node] = {
            "file": data.get("file"),
            "layer": data.get("layer"),
            "layer_rank": data.get("layer_rank"),
            "in_degree": dg._g.in_degree(node),
            "out_degree": dg._g.out_degree(node),
        }

    print("[ADG] Collecting edges…")
    edges = sorted([src, dst] for src, dst in dg._g.edges())

    print("[ADG] Building adjacency map…")
    adjacency = {}
    for node in sorted(dg._g.nodes()):
        adjacency[node] = {
            "imports": sorted(dg._g.successors(node)),
            "imported_by": sorted(dg._g.predecessors(node)),
        }

    print("[ADG] Collecting orphans…")
    orphans = dg.orphans()

    print("[ADG] Collecting cycles…")
    cycles = [sorted(c) for c in dg.cycles()]
    cycles.sort()

    print("[ADG] Collecting layer violations…")
    violations = [
        {"src": s, "dst": d, "src_layer": sl, "dst_layer": dl} for s, d, sl, dl in dg.layer_violations()
    ]

    print("[ADG] Collecting top fan-in / fan-out…")
    fan_in = [{"module": m, "count": c} for m, c in dg.fan_in_top(50)]
    fan_out = [{"module": m, "count": c} for m, c in dg.fan_out_top(50)]

    print("[ADG] Collecting syntax errors…")
    syntax_errors = [{"file": f, "error": e} for f, e in dg.syntax_errors()]

    built_at = datetime.now(timezone.utc).isoformat()

    payload = {
        "meta": {
            "built_at": built_at,
            "scan_roots": SSOT_DIRS,
            "force_rebuild": force_rebuild,
            "adg_source": "tools/dep_graph_db.py",
        },
        "stats": stats,
        "nodes": nodes,
        "edges": edges,
        "adjacency": adjacency,
        "orphans": orphans,
        "cycles": cycles,
        "layer_violations": violations,
        "fan_in_top50": fan_in,
        "fan_out_top50": fan_out,
        "syntax_errors": syntax_errors,
        "module_to_file": dict(sorted(dg._module_to_file.items())),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = OUT_DIR / f"adg_full_{ts}.json"

    print(f"[ADG] Writing {out_path} …")
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    size_kb = out_path.stat().st_size // 1024
    print(f"[ADG] Done. {out_path.name}  ({size_kb} KB)")
    print(f"      nodes={stats['total_nodes']}  edges={stats['total_edges']}")
    print(f"      orphans={stats['orphan_count']}  cycles={stats['cycle_count']}")
    print(f"      layer_violations={stats['layer_violation_count']}")
    print(f"      syntax_errors={stats['syntax_error_count']}")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Dump full ADG to JSON")
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Force a full re-parse of all source files (ignores SQLite cache)",
    )
    args = parser.parse_args()
    _dump(force_rebuild=args.rebuild)


if __name__ == "__main__":
    main()
