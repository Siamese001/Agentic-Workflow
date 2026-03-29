"""Census of route-like call symbols — finds candidates for _GOVERNANCE_ROUTE_SYMBOLS."""
import glob
import os
import sqlite3

adg_dir = os.path.join(os.path.dirname(__file__), "..", "artifacts", "adg")
db = sorted(glob.glob(os.path.join(adg_dir, "adg_indexed_*.sqlite")))[-1]
print(f"DB: {db}")
conn = sqlite3.connect(db)

rt = conn.execute("SELECT COUNT(*) FROM edges WHERE relation_type='routes_through'").fetchone()[0]
calls = conn.execute("SELECT COUNT(*) FROM edges WHERE relation_type='calls'").fetchone()[0]
print(f"Current: routes_through={rt}, calls={calls}, ratio={rt/calls*100:.2f}%\n")

has_rt = {r[0] for r in conn.execute(
    "SELECT DISTINCT source_file FROM edges WHERE relation_type='routes_through'"
).fetchall()}

route_keywords = [
    "route", "Route", "dispatch", "Dispatch", "orchestrat", "Orchestrat",
    "gateway", "Gateway", "pipeline", "Pipeline", "chain", "Chain",
    "forward", "Forward", "delegate", "Delegate", "broker", "Broker",
    "schedule", "Schedule", "coordinate", "Coordinate",
    "invoke", "Invoke", "relay", "Relay",
]

seen = {}
for kw in route_keywords:
    rows = conn.execute(f"""
        SELECT symbol, COUNT(*) as cnt, COUNT(DISTINCT source_file) as mod_cnt
        FROM edges WHERE relation_type='calls' AND symbol LIKE '%{kw}%'
        AND symbol NOT LIKE '%_emit_%'
        GROUP BY symbol HAVING cnt >= 3
        ORDER BY mod_cnt DESC LIMIT 10
    """).fetchall()
    for sym, cnt, mod_cnt in rows:
        tail = sym.split(".")[-1]
        if tail in seen:
            continue
        new_mods = conn.execute("""
            SELECT COUNT(DISTINCT source_file) FROM edges
            WHERE relation_type='calls' AND symbol=?
            AND source_file NOT IN (
                SELECT DISTINCT source_file FROM edges WHERE relation_type='routes_through'
            )
        """, (sym,)).fetchone()[0]
        if new_mods > 0:
            seen[tail] = (tail, cnt, mod_cnt, new_mods)

sorted_results = sorted(seen.values(), key=lambda x: -x[3])[:25]
print("Top 25 route-like symbols by new module coverage:")
for tail, cnt, mod_cnt, new_mods in sorted_results:
    print(f"  {tail:<50s} new_modules={new_mods:>4d}  total_calls={cnt:>4d}")

conn.close()
