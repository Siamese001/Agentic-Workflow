import glob
import sqlite3

files = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))
db = files[-1]
print(f"DB: {db}\n")

con = sqlite3.connect(db)
cur = con.cursor()

print("=== P0/L0 CLOSURE CRITERIA ===")
signals = {
    "emits_replay_key": ("L0 + all prod", None),
    "emits_determinism_digest": ("L0 + all prod", None),
    "records_execution_trace": ("L0", "L0"),
    "signs_execution_trace": ("L0", "L0"),
    "routes_path": ("L0", "L0"),
    "routes_through": ("L0", "L0"),
    "guards_replay": ("L0", "L0"),
    "uses_wall_clock": ("L0 routing (MUST=0)", "L0_routing_engines"),
    "invokes_getattr_dynamic": ("L0 routing engines (MUST=0)", "L0_routing_engines"),
}

for sig in [
    "emits_replay_key",
    "emits_determinism_digest",
    "records_execution_trace",
    "signs_execution_trace",
    "routes_path",
    "routes_through",
    "guards_replay",
]:
    cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type=?", (sig,))
    total = cur.fetchone()[0]
    cur.execute(
        """
        SELECT COUNT(*) FROM edges e JOIN nodes n ON e.src_id=n.id
        WHERE e.relation_type=? AND n.layer='L0'
    """,
        (sig,),
    )
    l0 = cur.fetchone()[0]
    print(f"  {sig:<35} total={total:4d}  L0={l0:3d}")

print()
cur.execute("""
    SELECT COUNT(*) FROM edges e JOIN nodes n ON e.src_id=n.id
    WHERE e.relation_type='uses_wall_clock'
    AND n.layer='L0'
    AND e.source_file NOT LIKE '%test%'
""")
wc = cur.fetchone()[0]
print(f"  uses_wall_clock L0 prod          = {wc}  (target=0)")

cur.execute("""
    SELECT COUNT(*) FROM edges e JOIN nodes n ON e.src_id=n.id
    WHERE e.relation_type='invokes_getattr_dynamic'
    AND n.layer='L0'
    AND e.source_file LIKE '%L0_routing/engines/%'
""")
dyn = cur.fetchone()[0]
print(f"  invokes_getattr_dynamic L0 engs  = {dyn}  (target=0)")

print()
print("=== ROUTING COVERAGE RATIO ===")
cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type IN ('routes_path','routes_through')")
routing = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type='emits_replay_key'")
rk = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type='emits_determinism_digest'")
dd = cur.fetchone()[0]
print(f"  routing_decisions = {routing}")
print(f"  emits_replay_key  = {rk}")
print(f"  emits_determinism = {dd}")
if routing > 0:
    print(f"  replay_coverage   = {rk / routing:.1%}  (target>=95%)")
    print(f"  digest_coverage   = {dd / routing:.1%}  (target>=95%)")

print()
print("=== L0 SIGNAL SOURCES (routes_path) ===")
cur.execute("""
    SELECT e.source_file, COUNT(*) as cnt
    FROM edges e JOIN nodes n ON e.src_id=n.id
    WHERE e.relation_type='routes_path' AND n.layer='L0'
    GROUP BY e.source_file ORDER BY cnt DESC LIMIT 15
""")
for r in cur.fetchall():
    print(f"  {r[0][:80]}  cnt={r[1]}")

print()
print("=== L0 SIGNAL SOURCES (emits_replay_key) ===")
cur.execute("""
    SELECT e.source_file, COUNT(*) as cnt
    FROM edges e JOIN nodes n ON e.src_id=n.id
    WHERE e.relation_type='emits_replay_key' AND n.layer='L0'
    GROUP BY e.source_file ORDER BY cnt DESC LIMIT 10
""")
for r in cur.fetchall():
    print(f"  {r[0][:80]}  cnt={r[1]}")

print()
print("=== L0 SIGNAL SOURCES (records_execution_trace) ===")
cur.execute("""
    SELECT e.source_file, COUNT(*) as cnt
    FROM edges e JOIN nodes n ON e.src_id=n.id
    WHERE e.relation_type='records_execution_trace' AND n.layer='L0'
    GROUP BY e.source_file ORDER BY cnt DESC LIMIT 10
""")
for r in cur.fetchall():
    print(f"  {r[0][:80]}  cnt={r[1]}")

print()
print("=== NEW VIOLATIONS (+3) ===")
cur.execute("""
    SELECT e.source_file, e.relation_type, e.symbol
    FROM edges e WHERE e.relation_type='violates'
    ORDER BY e.source_file
    LIMIT 15
""")
for r in cur.fetchall():
    print(f"  {r[0][:70]}  rel={r[1]}  sym={r[2]}")

con.close()
