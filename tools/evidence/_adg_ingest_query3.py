"""Get violations details and execute_ssot dead imports."""

import sqlite3
from pathlib import Path

db = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"), reverse=True)[0]
print(f"DB: {db.name}")
conn = sqlite3.connect(str(db))
conn.row_factory = sqlite3.Row


def node_name(nid):
    r = conn.execute("SELECT adg_name, resolved_path, layer FROM nodes WHERE id=?", (nid,)).fetchone()
    if r:
        return r["adg_name"], r["resolved_path"], r["layer"]
    return f"<id={nid}>", "", ""


# 1. ALL violates edges with full detail
rows = conn.execute(
    "SELECT src_id, dst_id, source_file, symbol, line_no FROM edges WHERE relation_type='violates'",
).fetchall()
print(f"\n=== ALL VIOLATIONS count={len(rows)} ===")
for r in rows:
    sn, sp, sl = node_name(r["src_id"])
    dn, dp, dl = node_name(r["dst_id"])
    print(f"  VIOLATION #{r['rowid'] if 'rowid' in r.keys() else '?'}")
    print(f"    SRC [{sl}]: {sp}")
    print(f"    DST [{dl}]: {dp}")
    print(f"    source_file={r['source_file']}  line={r['line_no']}")
    print(f"    sym={r['symbol']}")
    print()

# 2. execute_ssot dead imports
execute_ssot_node = conn.execute(
    "SELECT id FROM nodes WHERE adg_name='ADG::Module::agentic_core/L0_routing/scripts/execute_ssot.py'",
).fetchone()
if execute_ssot_node:
    eid = execute_ssot_node["id"]
    rows4 = conn.execute(
        "SELECT source_file, symbol, line_no FROM edges WHERE relation_type='dead_imports' AND src_id=? ORDER BY line_no",
        (eid,),
    ).fetchall()
    print(f"=== DEAD IMPORTS in execute_ssot count={len(rows4)} ===")
    for r in rows4:
        print(f"  line={r['line_no']:4d}  sym={r['symbol']}")

    # 3. antipatterns
    rows3 = conn.execute(
        "SELECT source_file, symbol, line_no FROM edges WHERE relation_type='antipattern' AND src_id=? ORDER BY line_no",
        (eid,),
    ).fetchall()
    print(f"\n=== ANTIPATTERNS in execute_ssot count={len(rows3)} ===")
    for r in rows3:
        print(f"  line={r['line_no']:4d}  sym={r['symbol']}")

# 4. _ssot_pipeline dead imports
pipe_node = conn.execute(
    "SELECT id FROM nodes WHERE adg_name='ADG::Module::agentic_core/L0_routing/scripts/_ssot_pipeline.py'",
).fetchone()
if pipe_node:
    pid = pipe_node["id"]
    rows5 = conn.execute(
        "SELECT symbol, line_no FROM edges WHERE relation_type='dead_imports' AND src_id=? ORDER BY line_no",
        (pid,),
    ).fetchall()
    print(f"\n=== DEAD IMPORTS in _ssot_pipeline count={len(rows5)} ===")
    for r in rows5:
        print(f"  line={r['line_no']:4d}  sym={r['symbol']}")

# 5. _ssot_validation_artifacts dead imports
va_node = conn.execute(
    "SELECT id FROM nodes WHERE adg_name='ADG::Module::agentic_core/L0_routing/scripts/_ssot_validation_artifacts.py'",
).fetchone()
if va_node:
    vid = va_node["id"]
    rows6 = conn.execute(
        "SELECT symbol, line_no FROM edges WHERE relation_type='dead_imports' AND src_id=? ORDER BY line_no",
        (vid,),
    ).fetchall()
    print(f"\n=== DEAD IMPORTS in _ssot_validation_artifacts count={len(rows6)} ===")
    for r in rows6:
        print(f"  line={r['line_no']:4d}  sym={r['symbol']}")

# 6. summary of E10 repair routes (look for them in meta table or edges)
meta_keys = conn.execute("SELECT key, value FROM meta ORDER BY key").fetchall()
print("\n=== ADG META ===")
for m in meta_keys:
    print(f"  {m['key']}: {m['value'][:200] if m['value'] else ''}")

conn.close()
print("\nDONE.")
