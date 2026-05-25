"""One-off probe: system_learning layer tags in latest ADG sqlite."""
from __future__ import annotations

import sqlite3
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ADG_DIR = REPO / "artifacts" / "adg"
db = max(ADG_DIR.glob("adg_indexed_*.sqlite"), key=lambda p: p.stat().st_mtime)
with sqlite3.connect(db) as conn:
    rows = conn.execute(
        """
        SELECT layer, COUNT(*) AS n
        FROM nodes
        WHERE resolved_path LIKE 'system_learning/%'
        GROUP BY layer
        ORDER BY n DESC
        """
    ).fetchall()
    print(db.name)
    for layer, n in rows:
        print(f"  {layer}: {n}")
    sample = conn.execute(
        """
        SELECT resolved_path, layer
        FROM nodes
        WHERE resolved_path LIKE 'system_learning/%'
        LIMIT 5
        """
    ).fetchall()
    print("sample:", sample)
