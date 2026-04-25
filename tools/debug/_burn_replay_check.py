"""Check replay_key.py import edges in latest snapshot."""

import sqlite3
from pathlib import Path

snap = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"), key=lambda x: x.stat().st_mtime)[-1]
print(f"snap: {snap.name}\n")
c = sqlite3.connect(str(snap))

# Find the replay_key node
row = c.execute(
    "SELECT id, resolved_path, layer FROM nodes WHERE resolved_path LIKE '%replay_key.py' AND entity_type='module'"
).fetchone()
print(f"node: {row}")

if row:
    node_id = row[0]
    # Find all importers
    importers = c.execute(
        """
        SELECT src.resolved_path, src.layer
        FROM edges e
        JOIN nodes src ON src.id = e.src_id
        WHERE e.dst_id = ? AND e.relation_type = 'imports'
        """,
        (node_id,),
    ).fetchall()
    print(f"\n{len(importers)} importers:")
    for p, l in importers:
        print(f"  [{l}] {p}")

    # Check __init__ import specifically
    init_row = c.execute(
        "SELECT id, layer FROM nodes WHERE resolved_path = 'agentic_core/L4_state/cache/__init__.py'"
    ).fetchone()
    print(f"\n__init__.py node: {init_row}")
