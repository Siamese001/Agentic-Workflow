"""Closure gap analysis for Waves 111-140.

Analyzes the real gap between denominators and numerators post-normalization.
Identifies false-negative symbols (real governed calls scanner misses)
and quantifies achievable closure without denominator growth.
"""
import glob
import os
import sqlite3

ADG_DIR = r"C:\Git\Agentic-Workflow\artifacts\adg"
files = sorted(glob.glob(os.path.join(ADG_DIR, "adg_indexed_*.sqlite")))
db_path = files[-1]
print(f"Using: {db_path}")

conn = sqlite3.connect(db_path)

# ── 1. reads_through / reads_from gap ──────────────────────────────────────

print("\n" + "="*70)
print("GAP 1: reads_through / reads_from")
print("="*70)

# What kind of reads_from edges exist?
rf_kinds = conn.execute(
    "SELECT edge_kind, COUNT(*) FROM edges WHERE relation_type='reads_from' GROUP BY edge_kind ORDER BY COUNT(*) DESC",
).fetchall()
print("\nreads_from by edge_kind:")
for kind, cnt in rf_kinds:
    print(f"  {kind}: {cnt:,}")

# How many modules have reads_from?
rf_modules = conn.execute("""
    SELECT COUNT(DISTINCT e.src_id) FROM edges e
    WHERE e.relation_type = 'reads_from'
""").fetchone()[0]
print(f"\nModules with reads_from: {rf_modules:,}")

# How many modules have reads_through?
rt_modules = conn.execute("""
    SELECT COUNT(DISTINCT e.src_id) FROM edges e
    WHERE e.relation_type = 'reads_through'
""").fetchone()[0]
print(f"Modules with reads_through: {rt_modules:,}")

# What symbols generate reads_through?
rt_symbols = conn.execute(
    "SELECT symbol, COUNT(*) FROM edges WHERE relation_type='reads_through' GROUP BY symbol ORDER BY COUNT(*) DESC LIMIT 20",
).fetchall()
print("\nreads_through symbols:")
for sym, cnt in rt_symbols:
    print(f"  {sym}: {cnt}")

# Look for potential false negatives: common read-like symbols in calls edges
print("\n--- Potential false-negative read symbols (in calls edges) ---")
read_candidates = conn.execute("""
    SELECT symbol, COUNT(*) FROM edges
    WHERE relation_type = 'calls'
      AND (symbol LIKE '%read%' OR symbol LIKE '%Read%' OR symbol LIKE '%fetch%'
           OR symbol LIKE '%query%' OR symbol LIKE '%get_state%' OR symbol LIKE '%load%')
      AND symbol NOT LIKE '_emit_%' AND symbol NOT LIKE 'emit_%'
    GROUP BY symbol ORDER BY COUNT(*) DESC LIMIT 30
""").fetchall()
for sym, cnt in read_candidates:
    print(f"  {sym}: {cnt}")

# ── 2. records_execution_trace / calls gap ─────────────────────────────────

print("\n" + "="*70)
print("GAP 2: records_execution_trace / calls")
print("="*70)

# What symbols generate records_execution_trace?
ret_symbols = conn.execute(
    "SELECT symbol, COUNT(*) FROM edges WHERE relation_type='records_execution_trace' GROUP BY symbol ORDER BY COUNT(*) DESC LIMIT 20",
).fetchall()
print(f"\nrecords_execution_trace symbols ({sum(c for _, c in ret_symbols)} total):")
for sym, cnt in ret_symbols:
    print(f"  {sym}: {cnt}")

# How many modules have records_execution_trace?
ret_modules = conn.execute("""
    SELECT COUNT(DISTINCT e.src_id) FROM edges e
    WHERE e.relation_type = 'records_execution_trace'
""").fetchone()[0]
print(f"\nModules with records_execution_trace: {ret_modules:,}")

# How many modules have calls?
calls_modules = conn.execute("""
    SELECT COUNT(DISTINCT e.src_id) FROM edges e
    WHERE e.relation_type = 'calls'
""").fetchone()[0]
print(f"Modules with calls: {calls_modules:,}")

# Look for potential false negatives: trace-like symbols in calls edges
print("\n--- Potential false-negative trace symbols (in calls edges) ---")
trace_candidates = conn.execute("""
    SELECT symbol, COUNT(*) FROM edges
    WHERE relation_type = 'calls'
      AND (symbol LIKE '%trace%' OR symbol LIKE '%Trace%'
           OR symbol LIKE '%execution_proof%' OR symbol LIKE '%ExecutionProof%'
           OR symbol LIKE '%record_trace%' OR symbol LIKE '%sign_trace%')
      AND symbol NOT LIKE '_emit_%' AND symbol NOT LIKE 'emit_%'
    GROUP BY symbol ORDER BY COUNT(*) DESC LIMIT 20
""").fetchall()
for sym, cnt in trace_candidates:
    print(f"  {sym}: {cnt}")

# ── 3. All governance numerator gaps ───────────────────────────────────────

print("\n" + "="*70)
print("ALL GOVERNANCE NUMERATOR COVERAGE")
print("="*70)

numerator_types = [
    ("writes_through", "writes_to"),
    ("reads_through", "reads_from"),
    ("routes_through", "calls"),
    ("pulls_context", "records_execution_trace"),
    ("emits_determinism_digest", "records_execution_trace"),
    ("signs_execution_trace", "records_execution_trace"),
    ("applies_guardrail", "calls"),
    ("snapshots_state", "calls"),
    ("emits_replay_key", "records_execution_trace"),
    ("execution_terminates_at_uwg", "calls"),
    ("validated_by_safety_plane", "applies_guardrail"),
]
for num_type, den_type in numerator_types:
    num_count = conn.execute(
        "SELECT COUNT(*) FROM edges WHERE relation_type=?", (num_type,),
    ).fetchone()[0]
    den_count = conn.execute(
        "SELECT COUNT(*) FROM edges WHERE relation_type=?", (den_type,),
    ).fetchone()[0]
    pct = num_count / den_count * 100 if den_count > 0 else 0
    print(f"  {num_type:40s} {num_count:>6,} / {den_count:>6,} = {pct:6.1f}%")

# ── 4. emits_metric_event check ───────────────────────────────────────────

print("\n" + "="*70)
print("SPECIAL: emits_metric_event (was 18,032, now 0)")
print("="*70)
eme = conn.execute(
    "SELECT COUNT(*) FROM edges WHERE relation_type='emits_metric_event'",
).fetchone()[0]
print(f"  emits_metric_event: {eme}")

# Check if there are metric-like calls we should be capturing
metric_candidates = conn.execute("""
    SELECT symbol, COUNT(*) FROM edges
    WHERE relation_type = 'calls'
      AND (symbol LIKE '%metric%' OR symbol LIKE '%Metric%'
           OR symbol LIKE '%telemetry%' OR symbol LIKE '%Telemetry%')
      AND symbol NOT LIKE '_emit_%' AND symbol NOT LIKE 'emit_%'
    GROUP BY symbol ORDER BY COUNT(*) DESC LIMIT 15
""").fetchall()
print("  Potential metric symbols in calls:")
for sym, cnt in metric_candidates:
    print(f"    {sym}: {cnt}")

conn.close()
