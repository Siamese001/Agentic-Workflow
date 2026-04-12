"""Query fresh ADG SQLite for violations, dead imports, repair routes, execute_ssot surface."""

import sqlite3
from pathlib import Path

db = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"), reverse=True)[0]
print(f"DB: {db.name}")
conn = sqlite3.connect(str(db))
conn.row_factory = sqlite3.Row


def node_name(nid):
    r = conn.execute("SELECT adg_name FROM nodes WHERE id=?", (nid,)).fetchone()
    return r["adg_name"] if r else f"<id={nid}>"


# 1. violates edges (critical)
rows = conn.execute(
    "SELECT src_id, dst_id, source_file, symbol FROM edges WHERE relation_type='violates' LIMIT 20",
).fetchall()
print(f"\n=== VIOLATIONS (GV) count={len(rows)} ===")
for r in rows:
    print(f"  SRC: {node_name(r['src_id'])}")
    print(f"  DST: {node_name(r['dst_id'])}")
    print(f"  file={r['source_file']}  sym={r['symbol']}")
    print()

# 2. repair routes
rows2 = conn.execute(
    "SELECT src_id, dst_id, relation_type, source_file, symbol FROM edges WHERE relation_type IN ('repair_route','has_repair_route','suggests_repair','repair_action') LIMIT 30",
).fetchall()
print(f"=== REPAIR ROUTES count={len(rows2)} ===")
for r in rows2:
    print(f"  {r['relation_type']}: {node_name(r['src_id'])} -> {node_name(r['dst_id'])}")

# 3. antipatterns involving execute_ssot
execute_ssot_node = conn.execute(
    "SELECT id FROM nodes WHERE adg_name='ADG::Module::agentic_core/L0_routing/scripts/execute_ssot.py'",
).fetchone()
if execute_ssot_node:
    eid = execute_ssot_node["id"]
    rows3 = conn.execute(
        "SELECT src_id, dst_id, source_file, symbol FROM edges WHERE relation_type='antipattern' AND (src_id=? OR dst_id=?) LIMIT 20",
        (eid, eid),
    ).fetchall()
    print(f"\n=== ANTIPATTERNS in execute_ssot count={len(rows3)} ===")
    for r in rows3:
        print(f"  file={r['source_file']} sym={r['symbol']}")

    # 4. dead imports in execute_ssot
    rows4 = conn.execute(
        "SELECT src_id, dst_id, source_file, symbol FROM edges WHERE relation_type='dead_imports' AND src_id=? LIMIT 20",
        (eid,),
    ).fetchall()
    print(f"\n=== DEAD IMPORTS in execute_ssot count={len(rows4)} ===")
    for r in rows4:
        print(f"  sym={r['symbol']}")

    # 5. execute_ssot imports (fan-out)
    rows5 = conn.execute(
        "SELECT dst_id FROM edges WHERE relation_type='imports' AND src_id=? LIMIT 60",
        (eid,),
    ).fetchall()
    print(f"\n=== execute_ssot IMPORTS count={len(rows5)} ===")
    for r in rows5:
        n = conn.execute("SELECT adg_name, resolved_path FROM nodes WHERE id=?", (r["dst_id"],)).fetchone()
        if n and "external" not in n["adg_name"]:
            print(f"  {n['adg_name']}")
else:
    print("  execute_ssot node NOT FOUND")

# 6. governance violations (GG plane)
rows7 = conn.execute(
    "SELECT src_id, dst_id, relation_type, source_file, symbol FROM edges WHERE relation_type IN ('governance_violation','layer_violation') LIMIT 20",
).fetchall()
print(f"\n=== GOVERNANCE VIOLATIONS count={len(rows7)} ===")
for r in rows7:
    print(
        f"  {r['relation_type']}: {node_name(r['src_id'])} -> {node_name(r['dst_id'])} | file={r['source_file']}",
    )

# 7. dead import hotspots (production files only, top 15)
rows8 = conn.execute(
    """SELECT n.resolved_path, COUNT(*) as cnt
       FROM edges e JOIN nodes n ON e.src_id=n.id
       WHERE e.relation_type='dead_imports'
         AND n.resolved_path NOT LIKE 'tests/%'
         AND n.resolved_path NOT LIKE 'ops_scripts/%'
       GROUP BY e.src_id ORDER BY cnt DESC LIMIT 15""",
).fetchall()
print("\n=== DEAD IMPORT HOTSPOTS (prod only) ===")
for r in rows8:
    print(f"  {r['cnt']:3d}  {r['resolved_path']}")

# 8. Layer violations (upward imports — L_high -> L_low)
rows9 = conn.execute(
    """SELECT n_src.layer as src_layer, n_src.resolved_path as src_path,
              n_dst.layer as dst_layer, n_dst.resolved_path as dst_path
       FROM edges e
       JOIN nodes n_src ON e.src_id = n_src.id
       JOIN nodes n_dst ON e.dst_id = n_dst.id
       WHERE e.relation_type = 'imports'
         AND n_src.resolved_path NOT LIKE 'tests/%'
         AND (
           (n_src.layer='L5' AND n_dst.layer IN ('L0','L1','L2','L3','L4'))
           OR (n_src.layer='L4' AND n_dst.layer IN ('L0','L1','L2','L3'))
           OR (n_src.layer='L3' AND n_dst.layer IN ('L0','L1','L2'))
           OR (n_src.layer='L2' AND n_dst.layer IN ('L0','L1'))
         )
       LIMIT 20""",
).fetchall()
print(f"\n=== UPWARD LAYER IMPORTS (gravity violations) count={len(rows9)} ===")
for r in rows9:
    print(f"  L{r['src_layer']}({r['src_path']}) -> L{r['dst_layer']}({r['dst_path']})")

conn.close()
print("\nDONE.")
