import sqlite3
from pathlib import Path

snap = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"), key=lambda x: x.stat().st_mtime)[-1]
print(f"snap: {snap.name}\n")
c = sqlite3.connect(str(snap))

# All nodes for replay_key.py
rows = c.execute(
    "SELECT id, entity_type, adg_name, layer FROM nodes WHERE resolved_path LIKE '%replay_key.py'"
).fetchall()
print(f"{len(rows)} nodes for replay_key.py:")
for nid, et, name, layer in rows:
    fin = c.execute(
        "SELECT COUNT(*) FROM edges WHERE dst_id=? AND relation_type='imports'",
        (nid,),
    ).fetchone()[0]
    print(f"  [{nid}] type={et:<12}  layer={layer}  fanin={fin}  name={name}")

# Show the __init__.py outgoing import edges
init_row = c.execute(
    "SELECT id FROM nodes WHERE resolved_path='agentic_core/L4_state/cache/__init__.py' AND entity_type='module'"
).fetchone()
print(f"\n__init__.py node: {init_row}")
if init_row:
    edges = c.execute(
        """
        SELECT e.edge_kind, dst.resolved_path, dst.entity_type, dst.adg_name
        FROM edges e JOIN nodes dst ON dst.id=e.dst_id
        WHERE e.src_id=? AND e.relation_type='imports' AND dst.resolved_path LIKE '%replay_key%'
        """,
        (init_row[0],),
    ).fetchall()
    print(f"__init__.py imports into replay_key*: {len(edges)}")
    for kind, rp, et, name in edges:
        print(f"  kind={kind}  dst={rp} ({et}) name={name}")
