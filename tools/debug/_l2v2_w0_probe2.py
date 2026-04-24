"""W0 supplemental probe — what views/relations actually exist."""

from __future__ import annotations
import glob, os, sqlite3

SNAP = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"), key=os.path.getmtime)[-1]
con = sqlite3.connect(SNAP)
cur = con.cursor()

# all edge relation types
cur.execute("SELECT relation_type, COUNT(*) FROM edges GROUP BY relation_type ORDER BY 2 DESC LIMIT 20")
print("Top 20 relation_types:")
for rel, n in cur.fetchall():
    print(f"  {rel}: {n}")

# all MV/view names
cur.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")
views = [r[0] for r in cur.fetchall()]
print(f"\nTotal views: {len(views)}")
print("mv_*:", [v for v in views if v.startswith("mv_")][:15])
print("v_p*:", [v for v in views if v.startswith("v_p")])

# SovereignBaseAgent — check for inheritance edges
cur.execute(
    "SELECT id FROM nodes WHERE resolved_path='agentic_core/base_agents/SovereignBaseAgent.py' AND entity_type='module'"
)
row = cur.fetchone()
if row:
    nid = row[0]
    cur.execute("""SELECT relation_type, COUNT(*) FROM edges WHERE dst_id=? GROUP BY relation_type""", (nid,))
    print(f"\nSovereignBaseAgent (module id={nid}) incoming edges by relation_type:")
    for rel, n in cur.fetchall():
        print(f"  {rel}: {n}")

# class-level: find SovereignBaseAgent class node
cur.execute("SELECT id, entity_type, adg_name FROM nodes WHERE adg_name='SovereignBaseAgent' LIMIT 5")
print("\nSovereignBaseAgent adg_name nodes:")
for nid, et, name in cur.fetchall():
    print(f"  id={nid} type={et} name={name}")
    cur.execute("SELECT relation_type, COUNT(*) FROM edges WHERE dst_id=? GROUP BY relation_type", (nid,))
    for rel, n in cur.fetchall():
        print(f"    incoming {rel}: {n}")

con.close()
