"""Inspect SC-1 / structural conformance schema in latest ADG snapshot."""

from __future__ import annotations

import sqlite3
from pathlib import Path

OUT = Path("artifacts/_sc1_schema.log")
OUT.parent.mkdir(parents=True, exist_ok=True)

snaps = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"))
if not snaps:
    OUT.write_text("no snapshots\n", encoding="utf-8")
    raise SystemExit(1)

snap = snaps[-1]
lines = [f"snapshot={snap.name}"]
con = sqlite3.connect(str(snap))
cur = con.cursor()

# All tables and views matching "structural" or "conformance"
cur.execute(
    "SELECT type, name FROM sqlite_master "
    "WHERE name LIKE '%structural%' OR name LIKE '%conformance%' "
    "ORDER BY type, name"
)
lines.append("\n== structural/conformance objects ==")
for typ, name in cur.fetchall():
    lines.append(f"{typ}\t{name}")

# Check v_structural_conformance schema
cur.execute("SELECT sql FROM sqlite_master WHERE name='v_structural_conformance'")
row = cur.fetchone()
if row:
    lines.append("\n== v_structural_conformance SQL ==")
    lines.append(row[0])
    try:
        cur.execute("SELECT COUNT(*) FROM v_structural_conformance")
        lines.append(f"\nrow_count={cur.fetchone()[0]}")
        cur.execute("SELECT * FROM v_structural_conformance LIMIT 3")
        cols = [d[0] for d in cur.description]
        lines.append(f"columns={cols}")
        lines.append("samples:")
        for r in cur.fetchall():
            lines.append(f"  {dict(zip(cols, r))}")
    except sqlite3.Error as e:
        lines.append(f"query error: {e}")
else:
    lines.append("\n!! v_structural_conformance not found !!")

# Look for any SC-1 specific views/tables
cur.execute(
    "SELECT type, name FROM sqlite_master "
    "WHERE name LIKE '%sc1%' OR name LIKE '%sc_1%' OR name LIKE '%sc-1%' "
    "OR name LIKE '%layer_gravity%' OR name LIKE '%import_cycle%' "
    "ORDER BY type, name"
)
lines.append("\n== SC-1 related objects ==")
for typ, name in cur.fetchall():
    lines.append(f"{typ}\t{name}")

OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
