"""Diff S2 violation counts per module between two ADG snapshots."""
from __future__ import annotations

import sqlite3
import sys
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


def counts(path: Path) -> Counter[str]:
    ph = ",".join("?" * len(ALLOW))
    conn = sqlite3.connect(path)
    rows = conn.execute(
        f"""
        SELECT src.resolved_path, COUNT(*)
        FROM edges e JOIN nodes src ON src.id = e.src_id
        WHERE e.relation_type = 'writes_to'
          AND src.resolved_path IS NOT NULL
          AND src.layer NOT IN ('L_TEST', 'L_TOOLS')
          AND src.resolved_path NOT IN ({ph})
        GROUP BY src.resolved_path
        """,
        tuple(ALLOW),
    ).fetchall()
    conn.close()
    return Counter({r[0]: r[1] for r in rows})


def main() -> int:
    old = REPO / (sys.argv[1] if len(sys.argv) > 1 else "artifacts/adg/adg_indexed_05252026_0634.sqlite")
    new = REPO / (sys.argv[2] if len(sys.argv) > 2 else "artifacts/adg/adg_indexed_05252026_1012.sqlite")
    a, b = counts(old), counts(new)
    print(f"old={old.name} total={sum(a.values())} new={new.name} total={sum(b.values())} delta={sum(b.values())-sum(a.values())}")
    gained = []
    for path in sorted(set(a) | set(b)):
        d = b[path] - a[path]
        if d != 0:
            gained.append((d, path, a[path], b[path]))
    gained.sort(reverse=True)
    for d, path, o, n in gained[:30]:
        print(f"{d:+4d}  was={o:3d} now={n:3d}  {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
