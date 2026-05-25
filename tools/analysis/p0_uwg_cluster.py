"""Cluster S2_uwg_bypass writes_to violations on latest or ADG_SNAPSHOT sqlite."""
from __future__ import annotations

import os
import sqlite3
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ALLOW = frozenset(
    {
        "agentic_core/L2_execution/utils/write_gateway.py",
        "agentic_core/L4_state/enforcement/promotion_write_gateway.py",
        "agentic_core/L5_safety/validators/static_checks/write_gateway_enforcer.py",
        "agentic_core/interfaces/write_gateway.py",
        "agentic_core/interfaces/write_gateway_shim.py",
    }
)
EXCLUDE = ("L_TEST", "L_TOOLS")


def _snap() -> Path:
    env = os.environ.get("ADG_SNAPSHOT")
    if env:
        return REPO / env
    adg = REPO / "artifacts" / "adg"
    files = sorted(adg.glob("adg_indexed_*.sqlite"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0]


def main() -> int:
    snap = _snap()
    conn = sqlite3.connect(snap)
    placeholders = ",".join("?" * len(ALLOW))
    q = f"""
        SELECT src.layer, src.resolved_path, e.symbol, COUNT(*) AS n
        FROM edges e
        JOIN nodes src ON src.id = e.src_id
        WHERE e.relation_type = 'writes_to'
          AND src.resolved_path IS NOT NULL
          AND src.layer NOT IN ('L_TEST', 'L_TOOLS')
          AND src.resolved_path NOT IN ({placeholders})
        GROUP BY src.layer, src.resolved_path, e.symbol
    """
    rows = conn.execute(q, tuple(ALLOW)).fetchall()
    conn.close()
    total = sum(r[3] for r in rows)
    by_mod: Counter[str] = Counter()
    by_layer: Counter[str] = Counter()
    for layer, path, _sym, n in rows:
        by_mod[path] += n
        by_layer[layer] += n
    print(f"snapshot={snap.name} violations={total}")
    print("by_layer:", dict(by_layer.most_common(8)))
    print("top_modules:")
    for path, n in by_mod.most_common(20):
        layer = next((r[0] for r in rows if r[1] == path), "?")
        print(f"  {n:4d} {layer:8s} {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
