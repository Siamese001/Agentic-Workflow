"""Phase 0/2 ADG audit: introspect schema, freshness, and view coverage.

Read-only SSOT-respecting probe. Run as:
    python tools/analysis/_audit_phase0_schema.py
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

DB = Path(r"C:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_04252026_0521.sqlite")
GRAPH = Path(r"C:\Git\Agentic-Workflow\artifacts\adg\adg_graph_04252026_0520.sqlite")


def introspect(path: Path, label: str) -> dict:
    if not path.exists():
        return {"label": label, "missing": True}
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    cur = con.cursor()
    tables = [
        r[0]
        for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
    ]
    views = [
        r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name").fetchall()
    ]
    counts: dict[str, int] = {}
    for t in tables:
        try:
            counts[t] = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        except sqlite3.OperationalError as exc:
            counts[t] = -1
    con.close()
    return {
        "label": label,
        "path": str(path),
        "size_bytes": path.stat().st_size,
        "table_count": len(tables),
        "view_count": len(views),
        "tables": tables,
        "views": views,
        "row_counts": counts,
    }


def main() -> int:
    out = {
        "indexed": introspect(DB, "indexed"),
        "graph": introspect(GRAPH, "graph"),
    }
    print(json.dumps(out, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
