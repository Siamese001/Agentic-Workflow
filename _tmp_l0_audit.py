import glob
import sqlite3

files = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))
db = files[-1]
print(f"DB: {db}\n")

con = sqlite3.connect(db)
cur = con.cursor()

print("=== L0 ROUTING: CURRENT SIGNAL COUNTS ===")
signals = [
    "routes_path",
    "routes_through",
    "emits_replay_key",
    "emits_determinism_digest",
    "records_execution_trace",
    "signs_execution_trace",
    "uses_wall_clock",
    "invokes_getattr_dynamic",
    "guards_replay",
]
for sig in signals:
    cur.execute(
        """
        SELECT COUNT(*) FROM edges e JOIN nodes n ON e.src_id=n.id
        WHERE e.relation_type=? AND n.layer='L0'
    """,
        (sig,),
    )
    cnt = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type=?", (sig,))
    total = cur.fetchone()[0]
    print(f"  L0: {sig:<35} prod={cnt:4d}  (total={total})")

print()
print("=== L0 ROUTING FILES ===")
cur.execute("""
    SELECT DISTINCT resolved_path FROM nodes
    WHERE layer='L0' AND entity_type='module' AND resolved_path != ''
    ORDER BY resolved_path
""")
l0_files = [r[0] for r in cur.fetchall()]
for f in l0_files:
    print(f"  {f}")

print()
print("=== wall_clock calls in routing files ===")
cur.execute("""
    SELECT e.source_file, e.line_no, e.symbol, COUNT(*)
    FROM edges e
    WHERE e.relation_type='uses_wall_clock'
    AND (e.source_file LIKE '%L0_routing%' OR e.source_file LIKE '%router%')
    GROUP BY e.source_file, e.line_no
    ORDER BY e.source_file
    LIMIT 30
""")
rows = cur.fetchall()
if rows:
    for r in rows:
        print(f"  {r[0][:70]}  line={r[1]}  sym={r[2]}")
else:
    print("  (none)")

print()
print("=== invokes_getattr_dynamic in L0 ===")
cur.execute("""
    SELECT e.source_file, e.line_no, e.symbol, COUNT(*)
    FROM edges e JOIN nodes n ON e.src_id=n.id
    WHERE e.relation_type='invokes_getattr_dynamic' AND n.layer='L0'
    GROUP BY e.source_file, e.line_no
    LIMIT 20
""")
rows = cur.fetchall()
if rows:
    for r in rows:
        print(f"  {r[0][:70]}  line={r[1]}  sym={r[2]}")
else:
    print("  (none)")

print()
print("=== routes_path / routes_through in L0 ===")
cur.execute("""
    SELECT e.source_file, e.relation_type, e.symbol, COUNT(*) as cnt
    FROM edges e JOIN nodes n ON e.src_id=n.id
    WHERE e.relation_type IN ('routes_path', 'routes_through') AND n.layer='L0'
    GROUP BY e.source_file, e.relation_type
    ORDER BY e.source_file
    LIMIT 20
""")
rows = cur.fetchall()
if rows:
    for r in rows:
        print(f"  {r[0][:70]}  rel={r[1]}  cnt={r[3]}")
else:
    print("  (none)")

con.close()
