# W6 ADG consumer mode declaration (per .cursor/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"

import sqlite3, glob, os

db = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"), key=os.path.getmtime)[-1]
con = sqlite3.connect(db)
cur = con.cursor()

print("=== nodes columns ===")
for r in cur.execute("PRAGMA table_info(nodes)"):
    print(f"  {r[1]:32s}  {r[2]}")

print("\n=== edges columns ===")
for r in cur.execute("PRAGMA table_info(edges)"):
    print(f"  {r[1]:32s}  {r[2]}")

print("\n=== violations columns ===")
for r in cur.execute("PRAGMA table_info(violations)"):
    print(f"  {r[1]:32s}  {r[2]}")

print("\n=== sample edge_kind values for imports ===")
for r in cur.execute(
    "SELECT edge_kind, COUNT(*) c FROM edges WHERE relation_type='imports' GROUP BY edge_kind ORDER BY c DESC"
):
    print(f"  {r[1]:6d}  edge_kind={r[0]}")

print("\n=== distinct entity_type values ===")
for r in cur.execute("SELECT entity_type, COUNT(*) c FROM nodes GROUP BY entity_type ORDER BY c DESC"):
    print(f"  {r[1]:6d}  {r[0]}")

print("\n=== distinct identity_kind values (top 15) ===")
for r in cur.execute(
    "SELECT identity_kind, COUNT(*) c FROM nodes GROUP BY identity_kind ORDER BY c DESC LIMIT 15"
):
    print(f"  {r[1]:6d}  {r[0]}")
