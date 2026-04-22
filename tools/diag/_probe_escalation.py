"""Probe: verify whether `escalation_router.py` truly has zero callers in ADG."""

from __future__ import annotations

import sqlite3
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
db = sorted((REPO / "artifacts" / "adg").glob("adg_indexed_*.sqlite"), key=lambda p: p.stat().st_mtime_ns)[-1]
conn = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
c = conn.cursor()

target = "agentic_core/L0_routing/reasoning/escalation_router.py"
print(f"Target: {target}\n")

c.execute("SELECT COUNT(*) FROM nodes WHERE resolved_path = ?", (target,))
print(f"  node count at this path: {c.fetchone()[0]}")

c.execute(
    "SELECT COUNT(*) FROM edges e JOIN nodes n ON e.dst_id = n.id "
    "WHERE e.relation_type = 'imports' AND n.resolved_path = ?",
    (target,),
)
print(f"  imports fan-in (all nodes at path): {c.fetchone()[0]}")

c.execute(
    "SELECT e.source_file FROM edges e JOIN nodes n ON e.dst_id = n.id "
    "WHERE e.relation_type = 'imports' AND n.resolved_path = ? LIMIT 10",
    (target,),
)
rows = c.fetchall()
if rows:
    print("  callers (up to 10):")
    for (src,) in rows:
        print(f"    {src}")

# Sanity: how many total import edges point to any agentic_core path?
c.execute(
    "SELECT COUNT(*) FROM edges e JOIN nodes n ON e.dst_id = n.id "
    "WHERE e.relation_type = 'imports' AND n.resolved_path LIKE 'agentic_core/%'"
)
print(f"\n  total imports edges into agentic_core/: {c.fetchone()[0]}")
