"""Census of read-like call symbols across the codebase — finds candidates for _GOVERNANCE_READ_SYMBOLS."""
import glob
import os
import sqlite3

adg_dir = os.path.join(os.path.dirname(__file__), "..", "artifacts", "adg")
db = sorted(glob.glob(os.path.join(adg_dir, "adg_indexed_*.sqlite")))[-1]
print(f"DB: {db}")
conn = sqlite3.connect(db)

# Current reads_through count
rt = conn.execute("SELECT COUNT(*) FROM edges WHERE relation_type='reads_through'").fetchone()[0]
rf = conn.execute("SELECT COUNT(*) FROM edges WHERE relation_type='reads_from'").fetchone()[0]
print(f"Current: reads_through={rt}, reads_from={rf}")

# Find call tails that look like reads
read_keywords = [
    "read", "Read", "load", "Load", "fetch", "Fetch",
    "get_config", "get_state", "get_cache",
    "query", "Query", "retrieve", "Retrieve",
    "parse", "Parse", "open",
    "Loader", "loader", "Reader", "reader",
]

for kw in read_keywords:
    rows = conn.execute(f"""
        SELECT symbol, COUNT(*) FROM edges
        WHERE relation_type='calls' AND symbol LIKE '%{kw}%'
        AND symbol NOT LIKE '%_emit_%'
        GROUP BY symbol ORDER BY COUNT(*) DESC LIMIT 5
    """).fetchall()
    if rows:
        total = sum(c for _, c in rows)
        print(f"\n  '{kw}' — {total} edges across {len(rows)} symbols (top 5):")
        for sym, cnt in rows:
            tail = sym.split(".")[-1]
            print(f"    {tail:<45s} count={cnt:>4d}")

# Show which scopes have the most reads_from but zero reads_through
print("\n\n=== SCOPE BREAKDOWN: reads_from modules with NO reads_through ===")
for scope, pattern in [
    ("apps_*", "apps_%"),
    ("tools/*", "tools/%"),
    ("ops_scripts/*", "ops_scripts/%"),
    ("agentic_core/*", "agentic_core/%"),
    ("system_learning/*", "system_learning/%"),
]:
    denom = conn.execute(f"""
        SELECT COUNT(DISTINCT source_file) FROM edges
        WHERE relation_type='reads_from' AND source_file LIKE '{pattern}'
        AND source_file NOT LIKE 'tests/%'
    """).fetchone()[0]
    numer = conn.execute(f"""
        SELECT COUNT(DISTINCT source_file) FROM edges
        WHERE relation_type='reads_through' AND source_file LIKE '{pattern}'
        AND source_file NOT LIKE 'tests/%'
    """).fetchone()[0]
    print(f"  {scope:<25s} reads_from: {denom:>5d} modules  reads_through: {numer:>5d}  gap: {denom - numer:>5d}")

conn.close()
