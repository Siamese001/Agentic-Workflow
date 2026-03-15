import glob
import sqlite3

db = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))[-1]
conn = sqlite3.connect(db)
c = conn.cursor()
c.execute(
    "SELECT DISTINCT symbol FROM edges WHERE source_file LIKE '%memory_authority%' ORDER BY symbol LIMIT 80"
)
print("=== memory_authority symbols ===")
for r in c.fetchall():
    print(r[0])
print("\n=== cache_backed search ===")
c.execute(
    "SELECT DISTINCT source_file, symbol FROM edges WHERE symbol LIKE '%cache%' AND source_file LIKE '%L4%' LIMIT 20"
)
for r in c.fetchall():
    print(r)
print("\n=== CACHE_BACKED search ===")
c.execute("SELECT DISTINCT source_file, symbol FROM edges WHERE symbol LIKE '%CACHE_BACKED%' LIMIT 20")
for r in c.fetchall():
    print(r)
conn.close()
