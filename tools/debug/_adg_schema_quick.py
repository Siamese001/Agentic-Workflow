import sqlite3
DB = "artifacts/adg/adg_indexed_04242026_0513.sqlite"
c = sqlite3.connect(DB)
cur = c.cursor()
print("=== TABLES ===")
for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall():
    print(" ", r[0])

for t in ("nodes", "edges"):
    print(f"\n=== {t} schema ===")
    for r in cur.execute(f"PRAGMA table_info({t})").fetchall():
        print(f"  {r[1]:<25} {r[2]}")

print("\n=== sample node ===")
for r in cur.execute("SELECT * FROM nodes LIMIT 1").fetchall():
    print(r)

print("\n=== distinct edges.relation_type ===")
for r in cur.execute("SELECT relation_type, COUNT(*) FROM edges GROUP BY relation_type ORDER BY 2 DESC LIMIT 30").fetchall():
    print(f"  {r[0]:<35} {r[1]}")

print("\n=== distinct nodes.layer ===")
for r in cur.execute("SELECT layer, COUNT(*) FROM nodes GROUP BY layer ORDER BY 2 DESC").fetchall():
    print(f"  {r[0]:<20} {r[1]}")
