"""Compare ADG snapshots before/after archival waves."""
from __future__ import annotations

import sqlite3
import sys

PRE = "artifacts/adg/adg_indexed_04232026_0925.sqlite"
POST = "artifacts/adg/adg_indexed_04232026_1418.sqlite"


def stats(path: str) -> dict[str, int]:
    c = sqlite3.connect(path)
    cur = c.cursor()
    cur.execute("SELECT COUNT(*) FROM nodes")
    nodes = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM edges")
    edges = cur.fetchone()[0]
    cur.execute("PRAGMA table_info(nodes)")
    cols = {r[1] for r in cur.fetchall()}
    modules = -1
    for cand in ("kind", "type", "node_type"):
        if cand in cols:
            cur.execute(f"SELECT COUNT(*) FROM nodes WHERE {cand}='module'")
            modules = cur.fetchone()[0]
            break
    violations = -1
    if _has_table(cur, "violations"):
        cur.execute("SELECT COUNT(*) FROM violations")
        violations = cur.fetchone()[0]
    c.close()
    return {"nodes": nodes, "modules": modules, "edges": edges, "violations": violations}


def _has_table(cur, name: str) -> bool:
    cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,))
    return cur.fetchone() is not None


a = stats(PRE)
b = stats(POST)
print(f"{'metric':<15} {'pre (0925)':>12} {'post (1418)':>12} {'delta':>10} {'pct':>7}")
for k in ("nodes", "modules", "edges", "violations"):
    av, bv = a[k], b[k]
    d = bv - av
    pct = (d / av * 100) if av > 0 else 0.0
    print(f"{k:<15} {av:>12,} {bv:>12,} {d:>+10,} {pct:>+6.2f}%")
