"""Diagnose G4, G8, G12 failures in the live SQLite artifact."""

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
db = sorted((ROOT / "artifacts" / "adg").glob("adg_indexed_*.sqlite"))[-1]
con = sqlite3.connect(db)
cur = con.cursor()

# ── G4: which __future__ dead_import edges exist? ──────────────────────────
print("=== G4: dead_imports with __future__ ===")
rows = cur.execute(
    "SELECT n1.adg_name, e.symbol, e.source_file, e.line_no "
    "FROM edges e JOIN nodes n1 ON n1.id=e.src_id "
    "WHERE e.relation_type='dead_imports' AND e.symbol LIKE '%__future__%'"
).fetchall()
for r in rows:
    print(f"  src={r[0]}")
    print(f"  sym={r[1]}")
    print(f"  file={r[2]}  line={r[3]}")
    print()

# ── G8: what adg_names exist for gateway-related nodes? ────────────────────
print("=== G8: gateway node search ===")
rows = cur.execute(
    "SELECT adg_name, entity_type, layer FROM nodes "
    "WHERE adg_name LIKE '%Gateway%' OR adg_name LIKE '%gateway%' LIMIT 10"
).fetchall()
for r in rows:
    print(f"  {r[0]}  type={r[1]}  layer={r[2]}")

# writes_through / routes_through edge targets (should be gateways)
print()
print("=== G8: writes_through / routes_through edge targets ===")
rows = cur.execute(
    "SELECT n2.adg_name, n2.entity_type, e.relation_type "
    "FROM edges e JOIN nodes n2 ON n2.id=e.dst_id "
    "WHERE e.relation_type IN ('writes_through','routes_through') LIMIT 10"
).fetchall()
for r in rows:
    print(f"  {r[0]}  type={r[1]}  rel={r[2]}")

# ── G12: belongs_to_layer - check if it appears in JSON artifact instead ───
print()
print("=== G12: belongs_to_layer anywhere? ===")
cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type='belongs_to_layer'")
print(f"  SQLite edges: {cur.fetchone()[0]}")

# Check file_graph JSON
import json

fgs = sorted((ROOT / "artifacts" / "adg").glob("adg_file_graph_*.json"))
if fgs:
    data = json.loads(fgs[-1].read_text(encoding="utf-8", errors="replace"))
    edges = data.get("edges", [])
    btl = [e for e in edges if e.get("relation_type") == "belongs_to_layer"]
    print(f"  file_graph JSON edges with belongs_to_layer: {len(btl)}")
    for e in btl[:3]:
        print(f"    {e.get('from_name', '?')} -> {e.get('to_name', '?')}")

# Also check snapshot
snaps = sorted((ROOT / "artifacts" / "adg").glob("adg_snapshot_*.json"))
if snaps:
    snap = json.loads(snaps[-1].read_text(encoding="utf-8", errors="replace"))
    # snapshot is a summary dict, check its keys
    print(f"  snapshot keys: {list(snap.keys())[:10]}")

con.close()
