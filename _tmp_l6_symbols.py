"""Inspect exact ADG symbol values for L6 evaluation_record symbols."""

import glob
import sqlite3

db = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))[-1]
conn = sqlite3.connect(db)
c = conn.cursor()

print(f"DB: {db}\n")

print("=== All symbols in evaluation_record.py ===")
c.execute(
    "SELECT DISTINCT symbol, relation_type FROM edges WHERE source_file LIKE '%evaluation_record%' ORDER BY symbol"
)
for r in c.fetchall():
    print(f"  {r[1]:<40} {r[0]}")

print("\n=== All symbols in evaluation_signal_integrator.py ===")
c.execute(
    "SELECT DISTINCT symbol, relation_type FROM edges WHERE source_file LIKE '%evaluation_signal_integrator%' ORDER BY symbol"
)
for r in c.fetchall():
    print(f"  {r[1]:<40} {r[0]}")

print("\n=== Sample invokes_eval edges (all, limit 5) ===")
c.execute("SELECT DISTINCT source_file, symbol FROM edges WHERE relation_type='invokes_eval' LIMIT 5")
for r in c.fetchall():
    print(f"  {r}")

print("\n=== Sample attaches_evaluation edges (all) ===")
c.execute("SELECT DISTINCT source_file, symbol FROM edges WHERE relation_type='attaches_evaluation'")
for r in c.fetchall():
    print(f"  {r}")
if not c.rowcount:
    print("  (none)")

print("\n=== Count of each relation_type for L6 evaluation files ===")
c.execute("""SELECT relation_type, COUNT(*) FROM edges
             WHERE source_file LIKE '%L6%'
             AND source_file NOT LIKE '%test%' AND source_file NOT LIKE '%tests%'
             GROUP BY relation_type ORDER BY COUNT(*) DESC LIMIT 20""")
for r in c.fetchall():
    print(f"  {r[0]:<45} {r[1]}")

conn.close()
