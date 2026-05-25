"""Retag system_learning nodes L_SL -> L6 in latest ADG sqlite (W1 seam)."""
from __future__ import annotations

import sqlite3
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ADG_DIR = REPO / "artifacts" / "adg"
db = max(ADG_DIR.glob("adg_indexed_*.sqlite"), key=lambda p: p.stat().st_mtime)
with sqlite3.connect(db) as conn:
    cur = conn.execute(
        """
        UPDATE nodes
        SET layer = 'L6'
        WHERE resolved_path LIKE 'system_learning/%' AND layer = 'L_SL'
        """
    )
    conn.commit()
    print(f"{db.name}: updated {cur.rowcount} node(s) L_SL -> L6")
