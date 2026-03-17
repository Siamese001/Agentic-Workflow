"""Census for remaining governance metrics — pulls_context, emits_determinism_digest,
validated_by_safety_plane, emits_metric_event, snapshots_state.

For each metric, find the schema.py frozenset that drives it and identify high-impact
symbols to add.
"""
import glob
import os
import sqlite3

adg_dir = os.path.join(os.path.dirname(__file__), "..", "artifacts", "adg")
db = sorted(glob.glob(os.path.join(adg_dir, "adg_indexed_*.sqlite")))[-1]
print(f"DB: {db}")
conn = sqlite3.connect(db)

# Show current state of all remaining metrics
metrics = [
    ("pulls_context", "records_execution_trace"),
    ("emits_determinism_digest", "records_execution_trace"),
    ("validated_by_safety_plane", "applies_guardrail"),
    ("emits_metric_event", "records_execution_trace"),
    ("snapshots_state", "calls"),
    ("execution_terminates_at_uwg", "calls"),
    ("emits_replay_key", "records_execution_trace"),
]

print("\n=== CURRENT METRIC STATE ===")
for numer, denom in metrics:
    n = conn.execute("SELECT COUNT(*) FROM edges WHERE relation_type=?", (numer,)).fetchone()[0]
    d = conn.execute("SELECT COUNT(*) FROM edges WHERE relation_type=?", (denom,)).fetchone()[0]
    n_mods = conn.execute("SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type=?", (numer,)).fetchone()[0]
    pct = n / d * 100 if d else 0
    print(f"  {numer:<35s} {n:>6,} edges  {n_mods:>4d} mods  ratio={pct:.2f}%")

# For each numerator, find which visitor generates it and what symbols drive it
# by looking at what symbols appear in calls edges that match semantic patterns
print("\n=== SAFETY PLANE SYMBOLS (validated_by_safety_plane) ===")
safety_kw = ["guard", "Guard", "safety", "Safety", "validate", "Validate", "breaker", "Breaker",
             "circuit", "Circuit", "sentinel", "Sentinel", "gate", "Gate", "enforce", "Enforce"]
has_vsp = {r[0] for r in conn.execute(
    "SELECT DISTINCT source_file FROM edges WHERE relation_type='validated_by_safety_plane'"
).fetchall()}
for kw in safety_kw:
    rows = conn.execute(f"""
        SELECT symbol, COUNT(DISTINCT source_file) as mod_cnt FROM edges
        WHERE relation_type='calls' AND symbol LIKE '%{kw}%'
        AND symbol NOT LIKE '%_emit_%'
        GROUP BY symbol HAVING mod_cnt >= 3
        ORDER BY mod_cnt DESC LIMIT 5
    """).fetchall()
    for sym, mod_cnt in rows:
        tail = sym.split(".")[-1]
        new = conn.execute("""
            SELECT COUNT(DISTINCT source_file) FROM edges
            WHERE relation_type='calls' AND symbol=?
            AND source_file NOT IN (SELECT DISTINCT source_file FROM edges WHERE relation_type='validated_by_safety_plane')
        """, (sym,)).fetchone()[0]
        if new >= 3:
            print(f"  {tail:<45s} new_mods={new:>4d}")

print("\n=== CONTEXT SYMBOLS (pulls_context) ===")
ctx_kw = ["context", "Context", "inject", "Inject", "resolve", "Resolve", "provide", "Provide",
          "session", "Session", "scope", "Scope"]
for kw in ctx_kw:
    rows = conn.execute(f"""
        SELECT symbol, COUNT(DISTINCT source_file) as mod_cnt FROM edges
        WHERE relation_type='calls' AND symbol LIKE '%{kw}%'
        AND symbol NOT LIKE '%_emit_%'
        GROUP BY symbol HAVING mod_cnt >= 3
        ORDER BY mod_cnt DESC LIMIT 5
    """).fetchall()
    for sym, mod_cnt in rows:
        tail = sym.split(".")[-1]
        new = conn.execute("""
            SELECT COUNT(DISTINCT source_file) FROM edges
            WHERE relation_type='calls' AND symbol=?
            AND source_file NOT IN (SELECT DISTINCT source_file FROM edges WHERE relation_type='pulls_context')
        """, (sym,)).fetchone()[0]
        if new >= 3:
            print(f"  {tail:<45s} new_mods={new:>4d}")

print("\n=== METRIC EVENT SYMBOLS (emits_metric_event) ===")
metric_kw = ["metric", "Metric", "telemetry", "Telemetry", "observ", "Observ",
             "monitor", "Monitor", "instrument", "Instrument", "measure", "Measure"]
for kw in metric_kw:
    rows = conn.execute(f"""
        SELECT symbol, COUNT(DISTINCT source_file) as mod_cnt FROM edges
        WHERE relation_type='calls' AND symbol LIKE '%{kw}%'
        AND symbol NOT LIKE '%_emit_%'
        GROUP BY symbol HAVING mod_cnt >= 3
        ORDER BY mod_cnt DESC LIMIT 5
    """).fetchall()
    for sym, mod_cnt in rows:
        tail = sym.split(".")[-1]
        new = conn.execute("""
            SELECT COUNT(DISTINCT source_file) FROM edges
            WHERE relation_type='calls' AND symbol=?
            AND source_file NOT IN (SELECT DISTINCT source_file FROM edges WHERE relation_type='emits_metric_event')
        """, (sym,)).fetchone()[0]
        if new >= 3:
            print(f"  {tail:<45s} new_mods={new:>4d}")

print("\n=== SNAPSHOT SYMBOLS (snapshots_state) ===")
snap_kw = ["snapshot", "Snapshot", "freeze", "Freeze", "checkpoint", "Checkpoint",
           "version", "Version", "baseline", "Baseline"]
for kw in snap_kw:
    rows = conn.execute(f"""
        SELECT symbol, COUNT(DISTINCT source_file) as mod_cnt FROM edges
        WHERE relation_type='calls' AND symbol LIKE '%{kw}%'
        AND symbol NOT LIKE '%_emit_%'
        GROUP BY symbol HAVING mod_cnt >= 3
        ORDER BY mod_cnt DESC LIMIT 5
    """).fetchall()
    for sym, mod_cnt in rows:
        tail = sym.split(".")[-1]
        new = conn.execute("""
            SELECT COUNT(DISTINCT source_file) FROM edges
            WHERE relation_type='calls' AND symbol=?
            AND source_file NOT IN (SELECT DISTINCT source_file FROM edges WHERE relation_type='snapshots_state')
        """, (sym,)).fetchone()[0]
        if new >= 3:
            print(f"  {tail:<45s} new_mods={new:>4d}")

conn.close()
