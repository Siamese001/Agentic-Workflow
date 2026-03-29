"""Measure the impact of adding a symbol to _GOVERNANCE_READ_SYMBOLS.

For each candidate symbol, counts how many DISTINCT modules would gain reads_through
if that symbol were added to the recognition set.
"""
import glob
import os
import sqlite3

adg_dir = os.path.join(os.path.dirname(__file__), "..", "artifacts", "adg")
db = sorted(glob.glob(os.path.join(adg_dir, "adg_indexed_*.sqlite")))[-1]
print(f"DB: {db}\n")
conn = sqlite3.connect(db)

# All candidate read symbols from calls edges, grouped by tail
rows = conn.execute("""
    SELECT symbol, COUNT(*) as cnt, COUNT(DISTINCT source_file) as mod_cnt
    FROM edges
    WHERE relation_type = 'calls'
    AND symbol NOT LIKE '%_emit_%'
    GROUP BY symbol
    HAVING cnt >= 3
    ORDER BY mod_cnt DESC
""").fetchall()

# Categorize by read-relevance
categories = {
    "config_readers": ["load", "Load", "config", "Config", "yaml", "json", "toml", "env", "settings", "hydrat"],
    "sqlite_readers": ["sqlite", "connect", "cursor", "execute", "fetchall", "fetchone", "query"],
    "redis_readers": ["redis", "Redis", "cache", "Cache", "hget", "get_redis"],
    "vector_readers": ["vector", "faiss", "embedding", "Embedding", "retriev", "Retriev", "similarity"],
    "artifact_readers": ["artifact", "Artifact", "archive", "bundle", "snapshot", "Snapshot", "report"],
    "file_readers": ["read", "Read", "open", "load_file", "read_text", "read_bytes", "Path"],
    "state_readers": ["state", "State", "freeze", "Freeze", "audit", "Audit", "payload"],
}

# Modules already having reads_through
has_rt = set(r[0] for r in conn.execute(
    "SELECT DISTINCT source_file FROM edges WHERE relation_type='reads_through'"
).fetchall())

for cat_name, keywords in categories.items():
    print(f"=== {cat_name} ===")
    candidates = []
    for sym, cnt, mod_cnt in rows:
        tail = sym.split(".")[-1]
        if any(kw.lower() in tail.lower() for kw in keywords):
            # Count new modules (not already having reads_through)
            new_mods = conn.execute("""
                SELECT COUNT(DISTINCT source_file) FROM edges
                WHERE relation_type='calls' AND symbol=?
                AND source_file NOT IN (
                    SELECT DISTINCT source_file FROM edges WHERE relation_type='reads_through'
                )
            """, (sym,)).fetchone()[0]
            if new_mods > 0:
                candidates.append((tail, sym, cnt, mod_cnt, new_mods))

    # Deduplicate by tail, keep highest impact
    seen_tails = {}
    for tail, sym, cnt, mod_cnt, new_mods in candidates:
        if tail not in seen_tails or new_mods > seen_tails[tail][4]:
            seen_tails[tail] = (tail, sym, cnt, mod_cnt, new_mods)

    sorted_cands = sorted(seen_tails.values(), key=lambda x: -x[4])[:10]
    for tail, sym, cnt, mod_cnt, new_mods in sorted_cands:
        print(f"  tail={tail:<45s} new_modules={new_mods:>4d}  total_calls={cnt:>4d}")

    print()

conn.close()
