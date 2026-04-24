import sqlite3

c = sqlite3.connect("artifacts/adg/adg_indexed_04242026_0721.sqlite")
cur = c.cursor()
cur.execute("PRAGMA table_info(nodes)")
cols = [r[1] for r in cur.fetchall()]
print("nodes columns:", cols)
cur.execute(
    "SELECT * FROM nodes "
    "WHERE adg_name LIKE '%CoverageAgent%' AND file_path LIKE '%L3_orchestration%reasoning%CoverageAgent%'"
)
nodes = cur.fetchall()
print("L3 CoverageAgent nodes:")
for r in nodes:
    print(" ", r)
ids = [r[0] for r in nodes]
if ids:
    ph = ",".join("?" * len(ids))
    cur.execute(
        f"SELECT src.file_path, src.adg_name, e.relation_type FROM edges e "
        f"JOIN nodes src ON e.src_id=src.id WHERE e.tgt_id IN ({ph}) LIMIT 30",
        ids,
    )
    rows = cur.fetchall()
    print(f"\nincoming edges ({len(rows)}):")
    for r in rows:
        print(" ", r)
