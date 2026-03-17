"""Census of write-like call symbols — finds candidates for _GOVERNANCE_WRITE_SYMBOLS."""
import glob
import os
import sqlite3

adg_dir = os.path.join(os.path.dirname(__file__), "..", "artifacts", "adg")
db = sorted(glob.glob(os.path.join(adg_dir, "adg_indexed_*.sqlite")))[-1]
print(f"DB: {db}")
conn = sqlite3.connect(db)

wt = conn.execute("SELECT COUNT(*) FROM edges WHERE relation_type='writes_through'").fetchone()[0]
wto = conn.execute("SELECT COUNT(*) FROM edges WHERE relation_type='writes_to'").fetchone()[0]
print(f"Current: writes_through={wt}, writes_to={wto}, ratio={wt/wto*100:.1f}%\n")

# Modules already having writes_through
has_wt = {r[0] for r in conn.execute(
    "SELECT DISTINCT source_file FROM edges WHERE relation_type='writes_through'"
).fetchall()}

# Find write-like symbols in calls edges
write_keywords = [
    "write", "Write", "save", "Save", "store", "Store",
    "persist", "Persist", "dump", "Dump", "emit", "Emit",
    "publish", "Publish", "send", "Send", "put", "Put",
    "insert", "Insert", "update", "Update", "create", "Create",
    "append", "Append", "log", "Log", "record", "Record",
    "commit", "Commit", "flush", "Flush",
]

seen = {}
for kw in write_keywords:
    rows = conn.execute(f"""
        SELECT symbol, COUNT(*) as cnt, COUNT(DISTINCT source_file) as mod_cnt
        FROM edges WHERE relation_type='calls' AND symbol LIKE '%{kw}%'
        AND symbol NOT LIKE '%_emit_%' AND symbol NOT LIKE '%emit_%'
        GROUP BY symbol HAVING cnt >= 3
        ORDER BY mod_cnt DESC LIMIT 10
    """).fetchall()
    for sym, cnt, mod_cnt in rows:
        tail = sym.split(".")[-1]
        if tail in seen:
            continue
        # Count new modules not already having writes_through
        new_mods = conn.execute("""
            SELECT COUNT(DISTINCT source_file) FROM edges
            WHERE relation_type='calls' AND symbol=?
            AND source_file NOT IN (
                SELECT DISTINCT source_file FROM edges WHERE relation_type='writes_through'
            )
        """, (sym,)).fetchone()[0]
        if new_mods > 0:
            seen[tail] = (tail, cnt, mod_cnt, new_mods)

sorted_results = sorted(seen.values(), key=lambda x: -x[3])[:30]
print("Top 30 write-like symbols by new module coverage:")
for tail, cnt, mod_cnt, new_mods in sorted_results:
    print(f"  {tail:<50s} new_modules={new_mods:>4d}  total_calls={cnt:>4d}  total_mods={mod_cnt:>4d}")

conn.close()
