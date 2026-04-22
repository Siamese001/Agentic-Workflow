"""Accurate orphan scan — queries ADG `imports` edges directly (no AST re-walk).

Replaces the inaccurate `scan_lazy_import_gaps.py` which rolled its own
top-level-only AST walk and over-reported orphans by ~188 modules
(see RCA RC2 retraction). This scanner:

1. Loads the latest `artifacts/adg/adg_indexed_*.sqlite` snapshot.
2. For every module node (entity_type='module') in agentic_core or apps_*,
   counts `imports` fan-in edges (all callers — top-level AND lazy).
3. Groups by layer and reports:
   - true zero-caller modules (fan-in == 0),
   - single-caller modules (fan-in == 1, fragile),
   - per-layer orphan counts.

No AST parsing, no double-counting. The source of truth is the ADG.
"""

from __future__ import annotations

import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _latest_snapshot() -> Path:
    candidates = sorted(
        (REPO / "artifacts" / "adg").glob("adg_indexed_*.sqlite"),
        key=lambda p: p.stat().st_mtime_ns,
    )
    if not candidates:
        raise SystemExit("No ADG snapshot found in artifacts/adg/")
    return candidates[-1]


def _layer_of(path: str) -> str:
    parts = path.replace("\\", "/").split("/")
    for p in parts:
        if p.startswith("L") and len(p) >= 2 and p[1].isdigit():
            return p.split("_")[0]
        if p.startswith("apps_"):
            return p
    return "?"


def main() -> int:
    db = _latest_snapshot()
    print(f"ADG snapshot: {db.name}\n")
    conn = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
    cur = conn.cursor()

    # All production module nodes with their imports fan-in.
    cur.execute(
        """
        SELECT
            n_adapter.resolved_path,
            (
                SELECT COUNT(*)
                FROM edges e
                JOIN nodes n_node ON e.dst_id = n_node.id
                WHERE e.relation_type = 'imports'
                  AND n_node.resolved_path = n_adapter.resolved_path
            ) AS fanin
        FROM nodes n_adapter
        WHERE n_adapter.entity_type = 'module'
          AND (
            n_adapter.resolved_path LIKE 'agentic_core/%'
            OR n_adapter.resolved_path LIKE 'apps_%/%'
          )
          AND n_adapter.resolved_path NOT LIKE '%/__init__.py'
          AND n_adapter.resolved_path NOT LIKE '%/__main__.py'
        """
    )
    rows = cur.fetchall()

    zero: list[tuple[str, int]] = []
    single: list[tuple[str, int]] = []
    by_layer: dict[str, int] = defaultdict(int)
    total = 0
    for path, fanin in rows:
        total += 1
        by_layer[_layer_of(path)] += 1
        if fanin == 0:
            zero.append((path, fanin))
        elif fanin == 1:
            single.append((path, fanin))

    print(f"Modules scanned: {total}")
    print(f"True zero-caller (ADG-verified): {len(zero)}")
    print(f"Single-caller (fragile — one edge from orphan): {len(single)}")
    print(f"\nPer-layer module count:")
    for layer in sorted(by_layer):
        print(f"  {layer:>12}: {by_layer[layer]}")

    print("\n" + "=" * 90)
    print("TRUE ZERO-CALLER MODULES (ADG-verified — no imports edges of any kind)")
    print("=" * 90)
    if not zero:
        print("  (none)")
    else:
        for path, _ in zero[:50]:
            layer = _layer_of(path)
            print(f"  {layer:>5}  {path}")

    print("\n" + "=" * 90)
    print("SINGLE-CALLER MODULES AT L0/L5 (×2.0 critical — one edge from orphan)")
    print("=" * 90)
    l0_l5_single = [(p, _layer_of(p)) for p, _ in single if _layer_of(p) in ("L0", "L5")]
    if not l0_l5_single:
        print("  (none)")
    else:
        for path, layer in sorted(l0_l5_single, key=lambda x: (x[1], x[0])):
            print(f"  {layer}  {path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
