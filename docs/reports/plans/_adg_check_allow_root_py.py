#!/usr/bin/env python3
"""Check ALLOW_ROOT_PY_TERRITORIES export status in structure_blueprint_config."""
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
db = sorted((ROOT / "artifacts/adg").glob("adg_indexed_*.sqlite"), reverse=True)[0]
con = sqlite3.connect(str(db))
con.row_factory = sqlite3.Row

def q(sql, params=()):
    return con.execute(sql, params).fetchall()

print("=== structure_blueprint_config.py all edges (source) ===")
rows = q("""
    SELECT e.relation_type, e.symbol, n_dst.adg_name
    FROM edges e
    LEFT JOIN nodes n_dst ON n_dst.id = e.dst_id
    WHERE e.source_file LIKE '%structure_blueprint_config.py'
      AND e.source_file NOT LIKE '%tests%'
    ORDER BY e.relation_type, e.symbol
""")
print(f"Total edges: {len(rows)}")
for r in rows[:60]:
    print(f"  [{r['relation_type']}] {r['symbol']}  dst={r['adg_name']}")
if len(rows) > 60:
    print(f"  ... {len(rows)-60} more")

print("\n=== ALLOW_ROOT_PY_TERRITORIES specifically ===")
arpt = q("""
    SELECT e.relation_type, e.source_file, e.symbol, n_dst.adg_name
    FROM edges e
    LEFT JOIN nodes n_dst ON n_dst.id = e.dst_id
    WHERE e.symbol LIKE '%ALLOW_ROOT_PY%'
""")
print(f"Any edge with ALLOW_ROOT_PY: {len(arpt)}")
for r in arpt:
    print(f"  [{r['relation_type']}] {r['source_file']}  [{r['symbol']}]")

print("\n=== Check __all__ in structure_blueprint_config (nodes) ===")
# Look for exports nodes from structure_blueprint_config
sbc_exports = q("""
    SELECT n.adg_name, n.entity_type, n.layer, n.resolved_path
    FROM nodes n
    WHERE n.resolved_path LIKE '%structure_blueprint_config.py'
      AND n.entity_type = 'symbol'
    ORDER BY n.adg_name
    LIMIT 60
""")
print(f"Symbol nodes in structure_blueprint_config: {len(sbc_exports)}")
for n in sbc_exports:
    print(f"  {n['adg_name']}")

con.close()
