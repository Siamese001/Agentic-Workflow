"""Get current state of all metrics below 100%."""
import sqlite3, glob, os

db = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"), key=os.path.getmtime)[-1]
conn = sqlite3.connect(db)
denom = conn.execute("SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type='calls'").fetchone()[0]
print(f"DB: {db}  Denom: {denom}\n")

rows = conn.execute("""
    SELECT relation_type, COUNT(DISTINCT source_file) as cnt
    FROM edges GROUP BY relation_type ORDER BY cnt DESC
""").fetchall()

below = []
at100 = 0
for rt, cnt in rows:
    r = cnt / denom * 100
    if r >= 100.0:
        at100 += 1
    else:
        below.append((rt, cnt, denom - cnt, r))

print(f"At 100%: {at100}")
print(f"Below 100%: {len(below)}\n")

for rt, cnt, gap, r in sorted(below, key=lambda x: -x[3]):
    print(f"  {rt:<45} {cnt:>5}/{denom}  gap={gap:>4}  {r:>6.2f}%")

# Check which are truly missing in source vs just stale ADG
print("\n--- Source verification for top gaps ---")
for rt, cnt, gap, r in sorted(below, key=lambda x: -x[3])[:10]:
    missing_mods = [row[0] for row in conn.execute("""
        SELECT DISTINCT e1.source_file FROM edges e1
        WHERE e1.relation_type='calls'
        AND e1.source_file NOT IN (
            SELECT DISTINCT e2.source_file FROM edges e2
            WHERE e2.relation_type=?
        )
    """, (rt,)).fetchall()]

    emitter = f"_emit_{rt}"
    truly_missing = 0
    for mod in missing_mods:
        try:
            with open(mod, "r", encoding="utf-8") as f:
                if emitter not in f.read():
                    truly_missing += 1
        except FileNotFoundError:
            pass
    print(f"  {rt:<40} ADG gap={gap:>4}  source gap={truly_missing:>4}")

conn.close()
