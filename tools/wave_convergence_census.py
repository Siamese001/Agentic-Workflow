"""Census for convergence wave planning — module coverage gaps by layer."""

import glob
import os
import sqlite3

db = sorted(glob.glob(os.path.join("artifacts", "adg", "adg_indexed_*.sqlite")))[-1]
conn = sqlite3.connect(db)
print(f"DB: {db}\n")

# Numerator metrics
nums = [
    "reads_through",
    "writes_through",
    "routes_through",
    "records_execution_trace",
    "snapshots_state",
    "emits_determinism_digest",
    "emits_metric_event",
    "pulls_context",
    "validated_by_safety_plane",
    "signs_execution_trace",
    "emits_replay_key",
    "execution_terminates_at_uwg",
]
# Denominator metrics
denoms = ["reads_from", "writes_to", "calls", "records_execution_trace", "applies_guardrail"]

print("=== NUMERATOR COVERAGE ===")
for rt in nums:
    edges = conn.execute("SELECT COUNT(*) FROM edges WHERE relation_type=?", (rt,)).fetchone()[0]
    mods = conn.execute(
        "SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type=?", (rt,)
    ).fetchone()[0]
    print(f"  {rt:40s}  edges={edges:>6,}  modules={mods:>5,}")

print("\n=== DENOMINATOR COVERAGE ===")
for rt in denoms:
    edges = conn.execute("SELECT COUNT(*) FROM edges WHERE relation_type=?", (rt,)).fetchone()[0]
    mods = conn.execute(
        "SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type=?", (rt,)
    ).fetchone()[0]
    print(f"  {rt:40s}  edges={edges:>6,}  modules={mods:>5,}")

# Module coverage ratios
print("\n=== MODULE COVERAGE RATIOS ===")
pairs = [
    ("reads_through", "reads_from"),
    ("writes_through", "writes_to"),
    ("routes_through", "calls"),
    ("records_execution_trace", "calls"),
    ("snapshots_state", "calls"),
    ("emits_determinism_digest", "records_execution_trace"),
    ("validated_by_safety_plane", "applies_guardrail"),
    ("pulls_context", "records_execution_trace"),
    ("emits_metric_event", "records_execution_trace"),
    ("signs_execution_trace", "records_execution_trace"),
]
for num_rt, den_rt in pairs:
    n_mod = conn.execute(
        "SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type=?", (num_rt,)
    ).fetchone()[0]
    d_mod = conn.execute(
        "SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type=?", (den_rt,)
    ).fetchone()[0]
    ratio = (n_mod / d_mod * 100) if d_mod else 0
    print(f"  {num_rt:35s} / {den_rt:25s} = {n_mod:>5,}/{d_mod:>5,} = {ratio:6.1f}% module coverage")

# Find top uncovered symbol opportunities for key gaps
print("\n=== TOP UNCOVERED SYMBOL OPPORTUNITIES ===")

# For reads_through: symbols called in modules WITH reads_from but WITHOUT reads_through
print("\n-- reads_through gap symbols (modules with reads_from but no reads_through) --")
rows = conn.execute("""
    SELECT e.symbol, COUNT(DISTINCT e.source_file) as new_mods
    FROM edges e
    WHERE e.relation_type = 'calls'
      AND e.source_file IN (
          SELECT DISTINCT source_file FROM edges WHERE relation_type='reads_from'
          EXCEPT
          SELECT DISTINCT source_file FROM edges WHERE relation_type='reads_through'
      )
    GROUP BY e.symbol
    ORDER BY new_mods DESC
    LIMIT 15
""").fetchall()
for sym, cnt in rows:
    print(f"  {sym:60s}  covers {cnt:>4} gap modules")

# For writes_through: symbols called in modules WITH writes_to but WITHOUT writes_through
print("\n-- writes_through gap symbols (modules with writes_to but no writes_through) --")
rows = conn.execute("""
    SELECT e.symbol, COUNT(DISTINCT e.source_file) as new_mods
    FROM edges e
    WHERE e.relation_type = 'calls'
      AND e.source_file IN (
          SELECT DISTINCT source_file FROM edges WHERE relation_type='writes_to'
          EXCEPT
          SELECT DISTINCT source_file FROM edges WHERE relation_type='writes_through'
      )
    GROUP BY e.symbol
    ORDER BY new_mods DESC
    LIMIT 15
""").fetchall()
for sym, cnt in rows:
    print(f"  {sym:60s}  covers {cnt:>4} gap modules")

# For routes_through: symbols called in modules WITH calls but WITHOUT routes_through
print("\n-- routes_through gap symbols (modules with calls but no routes_through) --")
rows = conn.execute("""
    SELECT e.symbol, COUNT(DISTINCT e.source_file) as new_mods
    FROM edges e
    WHERE e.relation_type = 'calls'
      AND e.source_file IN (
          SELECT DISTINCT source_file FROM edges WHERE relation_type='calls'
          EXCEPT
          SELECT DISTINCT source_file FROM edges WHERE relation_type='routes_through'
      )
      AND (e.symbol LIKE '%route%' OR e.symbol LIKE '%dispatch%' OR e.symbol LIKE '%orchestrat%'
           OR e.symbol LIKE '%pipeline%' OR e.symbol LIKE '%gateway%' OR e.symbol LIKE '%forward%'
           OR e.symbol LIKE '%delegate%' OR e.symbol LIKE '%handler%' OR e.symbol LIKE '%invoke%')
    GROUP BY e.symbol
    ORDER BY new_mods DESC
    LIMIT 20
""").fetchall()
for sym, cnt in rows:
    print(f"  {sym:60s}  covers {cnt:>4} gap modules")

# For records_execution_trace: what symbols could add trace edges
print("\n-- execution trace gap symbols (broad trace/record/log patterns) --")
rows = conn.execute("""
    SELECT e.symbol, COUNT(DISTINCT e.source_file) as new_mods
    FROM edges e
    WHERE e.relation_type = 'calls'
      AND e.source_file NOT IN (
          SELECT DISTINCT source_file FROM edges WHERE relation_type='records_execution_trace'
      )
      AND (e.symbol LIKE '%trace%' OR e.symbol LIKE '%record%' OR e.symbol LIKE '%log%'
           OR e.symbol LIKE '%audit%' OR e.symbol LIKE '%proof%')
    GROUP BY e.symbol
    ORDER BY new_mods DESC
    LIMIT 20
""").fetchall()
for sym, cnt in rows:
    print(f"  {sym:60s}  covers {cnt:>4} gap modules")

# For snapshots_state
print("\n-- snapshots_state gap symbols --")
rows = conn.execute("""
    SELECT e.symbol, COUNT(DISTINCT e.source_file) as new_mods
    FROM edges e
    WHERE e.relation_type = 'calls'
      AND e.source_file NOT IN (
          SELECT DISTINCT source_file FROM edges WHERE relation_type='snapshots_state'
      )
      AND (e.symbol LIKE '%snapshot%' OR e.symbol LIKE '%state%' OR e.symbol LIKE '%freeze%'
           OR e.symbol LIKE '%checkpoint%' OR e.symbol LIKE '%persist%')
    GROUP BY e.symbol
    ORDER BY new_mods DESC
    LIMIT 15
""").fetchall()
for sym, cnt in rows:
    print(f"  {sym:60s}  covers {cnt:>4} gap modules")

conn.close()
