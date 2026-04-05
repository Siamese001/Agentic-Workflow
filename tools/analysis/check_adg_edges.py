"""Check ADG edges for specific files to diagnose scanner detection."""

import sqlite3
from pathlib import Path

db = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"))[-1]
conn = sqlite3.connect(str(db))
cur = conn.cursor()

target = "agentic_core/L0_routing/scripts/full_agent_discovery.py"
P0_RELS = [
    "emits_replay_key",
    "emits_determinism_digest",
    "applies_guardrail",
    "snapshots_state",
    "signs_execution_trace",
    "records_execution_trace",
]
cur.execute("SELECT relation_type, symbol, line_no FROM edges WHERE source_file = ?", (target,))
rows = cur.fetchall()
print(f"P0 edges for {target}:")
for r in rows:
    if r[0] in P0_RELS:
        print(f"  {r[0]:<40s} line={r[2]}  sym={r[1]}")

print()
for rel in ["emits_replay_key", "emits_determinism_digest"]:
    cur.execute("SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type = ?", (rel,))
    print(f"Modules with {rel}: {cur.fetchone()[0]}")

# Check scan_cache to see if these files are cached at old state
print()
try:
    cur.execute("PRAGMA table_info(scan_cache)")
    cache_cols = [c[1] for c in cur.fetchall()]
    print(f"scan_cache columns: {cache_cols}")
except (ValueError, TypeError, RuntimeError) as e:  # guardian: allow-silent-swallower -- diagnostic script; PRAGMA failure is non-fatal, error printed to stdout
    print(f"No scan_cache table: {e}")

conn.close()
