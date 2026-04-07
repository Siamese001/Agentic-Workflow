"""Check SQLite schema and governance graph structure."""

import json
import sqlite3
from pathlib import Path

db = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"))[-1]
conn = sqlite3.connect(str(db))

print("=== SQLITE TABLES ===")
for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
    print(f"  {row[0]}")
    cols = conn.execute(f"PRAGMA table_info({row[0]})").fetchall()
    for c in cols:
        print(f"    col: {c[1]} ({c[2]})")

conn.close()

# Also peek at governance graph for relation coverage
gov_files = sorted(Path("artifacts/adg").glob("adg_governance_graph_*.json"))
if gov_files:
    with open(gov_files[-1]) as f:
        gov = json.load(f)
    print()
    print("=== GOVERNANCE GRAPH TOP-LEVEL KEYS ===")
    print(list(gov.keys())[:20])
    if "edges" in gov:
        rels = {}
        for e in gov["edges"]:
            r = e.get("relation_type", "?")
            rels[r] = rels.get(r, 0) + 1
        print()
        print("=== GOVERNANCE GRAPH RELATION TYPES BY COUNT ===")
        for r, cnt in sorted(rels.items(), key=lambda x: -x[1]):
            print(f"  {cnt:6d}  {r}")
