import glob
import sqlite3

files = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))
db = files[-1]
con = sqlite3.connect(db)
cur = con.cursor()

print("=== REPLAY/DETERMINISM SIGNAL COVERAGE IN L0 ===")
for sig in [
    "emits_replay_key",
    "emits_determinism_digest",
    "records_execution_trace",
    "signs_execution_trace",
    "routes_path",
    "routes_through",
]:
    cur.execute(
        """
        SELECT COUNT(*)
        FROM edges e JOIN nodes n ON e.src_id=n.id
        WHERE e.relation_type=? AND n.layer='L0'
    """,
        (sig,),
    )
    cnt = cur.fetchone()[0]
    print(f"  L0 {sig:<35} count={cnt}")

print()
print("=== WHAT SCANNER DETECTS FOR emit_replay_key IN ANY FILE ===")
cur.execute("""
    SELECT e.source_file, e.line_no, e.symbol
    FROM edges e
    WHERE e.relation_type='emits_replay_key'
    LIMIT 20
""")
for r in cur.fetchall():
    print(f"  {r[0][:70]}  line={r[1]}  sym={r[2]}")

print()
print("=== ROUTING DECISIONS (routes_path + routes_through) ALL LAYERS ===")
cur.execute("""
    SELECT n.layer, e.source_file, e.relation_type, COUNT(*)
    FROM edges e JOIN nodes n ON e.src_id=n.id
    WHERE e.relation_type IN ('routes_path','routes_through')
    GROUP BY n.layer, e.source_file, e.relation_type
    ORDER BY n.layer
    LIMIT 20
""")
for r in cur.fetchall():
    print(f"  layer={r[0]}  {r[2]}  src={r[1][:60] if r[1] else None}  cnt={r[3]}")

print()
print("=== WALL CLOCK IN L0 ROUTING FILES (by file) ===")
cur.execute("""
    SELECT e.source_file, e.line_no, e.symbol
    FROM edges e
    WHERE e.relation_type='uses_wall_clock'
    AND (e.source_file LIKE '%L0_routing%')
    ORDER BY e.source_file, e.line_no
    LIMIT 30
""")
for r in cur.fetchall():
    print(f"  {r[0][:70]}  line={r[1]}  sym={r[2]}")

print()
print("=== WHAT SCHEMA SAYS for ROUTING SYMBOLS ===")
import re

with open("agentic_core/adg/schema.py", encoding="utf-8") as f:
    txt = f.read()
for name in [
    "ROUTING_PATH_CLASSES",
    "ROUTING_PATH_METHODS",
    "REPLAY_KEY_METHODS",
    "PATH_CONTROL_CLASSES",
    "PATH_REROUTE_METHODS",
]:
    m = re.search(rf"{re.escape(name)}\s*(?::[^\n=]*)?\s*=", txt)
    if m:
        block = txt[m.start() : m.start() + 400]
        print(f"\n{name}:")
        print(block[:350])
    else:
        print(f"\n{name}: NOT FOUND")

con.close()
