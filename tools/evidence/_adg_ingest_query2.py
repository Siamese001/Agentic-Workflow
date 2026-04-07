"""Query violations and execute_ssot dead imports specifically."""

import sqlite3
from pathlib import Path

db = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"), reverse=True)[0]
print(f"DB: {db.name}")
conn = sqlite3.connect(str(db))
conn.row_factory = sqlite3.Row


def node_name(nid):
    r = conn.execute("SELECT adg_name, resolved_path FROM nodes WHERE id=?", (nid,)).fetchone()
    if r:
        return r["adg_name"], r["resolved_path"]
    return f"<id={nid}>", ""


# 1. violates edges
rows = conn.execute(
    "SELECT src_id, dst_id, source_file, symbol FROM edges WHERE relation_type='violates' LIMIT 20",
).fetchall()
print(f"\n=== VIOLATIONS count={len(rows)} ===")
for r in rows:
    sn, sp = node_name(r["src_id"])
    dn, dp = node_name(r["dst_id"])
    print(f"  SRC: {sn}  path={sp}")
    print(f"  DST: {dn}  path={dp}")
    print(f"  source_file={r['source_file']}  sym={r['symbol']}")
    print()

# 2. dead imports in execute_ssot
execute_ssot_node = conn.execute(
    "SELECT id FROM nodes WHERE adg_name='ADG::Module::agentic_core/L0_routing/scripts/execute_ssot.py'",
).fetchone()
if execute_ssot_node:
    eid = execute_ssot_node["id"]
    rows4 = conn.execute(
        "SELECT source_file, symbol, line_no FROM edges WHERE relation_type='dead_imports' AND src_id=? ORDER BY symbol",
        (eid,),
    ).fetchall()
    print(f"=== DEAD IMPORTS in execute_ssot count={len(rows4)} ===")
    for r in rows4:
        print(f"  line={r['line_no']:4d}  sym={r['symbol']}")

    # antipatterns
    rows3 = conn.execute(
        "SELECT source_file, symbol, line_no FROM edges WHERE relation_type='antipattern' AND src_id=? ORDER BY symbol",
        (eid,),
    ).fetchall()
    print(f"\n=== ANTIPATTERNS in execute_ssot count={len(rows3)} ===")
    for r in rows3:
        print(f"  line={r['line_no']:4d}  sym={r['symbol']}")

# 3. Top dead import files across whole repo (production only), with symbols
rows8 = conn.execute(
    """SELECT n.resolved_path, e.symbol, e.line_no
       FROM edges e JOIN nodes n ON e.src_id=n.id
       WHERE e.relation_type='dead_imports'
         AND n.resolved_path NOT LIKE 'tests/%'
         AND n.resolved_path NOT LIKE 'ops_scripts/%'
         AND n.resolved_path LIKE 'agentic_core/adg/runtime/__init__.py'
       ORDER BY e.line_no""",
).fetchall()
print(f"\n=== DEAD IMPORTS in agentic_core/adg/runtime/__init__.py count={len(rows8)} ===")
for r in rows8:
    print(f"  line={r['line_no']:4d}  sym={r['symbol']}")

# 4. adg/runtime/__init__.py issues
rows9 = conn.execute(
    """SELECT n.resolved_path, e.symbol, e.line_no
       FROM edges e JOIN nodes n ON e.src_id=n.id
       WHERE e.relation_type='dead_imports'
         AND n.resolved_path = 'agentic_core/adg/runtime/__init__.py'
       ORDER BY e.line_no""",
).fetchall()
print(f"\n=== agentic_core/adg/runtime/__init__.py dead imports count={len(rows9)} ===")
for r in rows9:
    print(f"  line={r['line_no']:4d}  sym={r['symbol']}")

conn.close()
print("\nDONE.")
