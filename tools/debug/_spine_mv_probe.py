"""Probe: why does mv_runtime_spine_gaps report 100% disconnection on every layer?"""
import sqlite3
from pathlib import Path

snap = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"), key=lambda p: p.stat().st_mtime)[-1]
print(f"Snapshot: {snap.name}\n")
conn = sqlite3.connect(snap)

print("== total modules by layer (spine-eligible) ==")
for row in conn.execute(
    "SELECT layer, COUNT(*) FROM nodes WHERE entity_type='module' "
    "AND layer IN ('L0','L1','L2','L3','L4','L5','L6','L_APP','L_SHARED') "
    "AND resolved_path NOT LIKE 'tests/%' AND resolved_path NOT LIKE 'tools/%' "
    "GROUP BY layer ORDER BY 2 DESC"
):
    print(f"  {row[0]:10s} {row[1]}")

print("\n== count of import edges whose dst is a module node ==")
row = conn.execute(
    "SELECT COUNT(*) FROM edges e JOIN nodes dst ON dst.id=e.dst_id "
    "WHERE e.relation_type IN ('imports','calls') AND dst.entity_type='module'"
).fetchone()
print(f"  module-targeted edges: {row[0]}")

row = conn.execute(
    "SELECT COUNT(*) FROM edges e JOIN nodes dst ON dst.id=e.dst_id "
    "WHERE e.relation_type IN ('imports','calls') AND dst.entity_type='symbol'"
).fetchone()
print(f"  symbol-targeted edges: {row[0]}")

print("\n== mv_runtime_spine_gaps rows ==")
for row in conn.execute("SELECT layer, module_count, connected_count, gap_count, gap_pct FROM mv_runtime_spine_gaps"):
    print(f"  {row[0]:10s} mod={row[1]:4d} conn={row[2]:4d} gap={row[3]:4d} pct={row[4]}")

print("\n== sample: pick one module that IS imported and check the edge target entity_type ==")
row = conn.execute(
    "SELECT n.id, n.resolved_path, n.layer FROM nodes n WHERE n.entity_type='module' "
    "AND n.layer='L0' AND n.resolved_path LIKE '%path_constants%' LIMIT 1"
).fetchone()
if row:
    mid, path, layer = row
    print(f"  module node: id={mid}, path={path}, layer={layer}")
    fan = conn.execute("SELECT COUNT(*) FROM edges WHERE dst_id=? AND relation_type='imports'", (mid,)).fetchone()[0]
    print(f"  inbound imports edges (dst=module_id): {fan}")
    # Inbound via any symbol owned by this module
    fan2 = conn.execute(
        "SELECT COUNT(*) FROM edges e JOIN nodes dst ON dst.id=e.dst_id "
        "WHERE e.relation_type='imports' AND dst.resolved_path=?",
        (path,)
    ).fetchone()[0]
    print(f"  inbound imports edges (dst.resolved_path=module): {fan2}")
