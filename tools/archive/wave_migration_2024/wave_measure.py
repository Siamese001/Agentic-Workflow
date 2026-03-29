"""Measure current reads_through and all denominator/numerator state after a wave."""
import glob
import os
import sqlite3

adg_dir = os.path.join(os.path.dirname(__file__), "..", "artifacts", "adg")
db = sorted(glob.glob(os.path.join(adg_dir, "adg_indexed_*.sqlite")))[-1]
print(f"DB: {db}")
conn = sqlite3.connect(db)

# All governance edge types
types = [
    "writes_to", "reads_from", "records_execution_trace", "calls",
    "applies_guardrail",
    "writes_through", "reads_through", "routes_through",
    "pulls_context", "emits_determinism_digest", "signs_execution_trace",
    "snapshots_state", "emits_replay_key", "execution_terminates_at_uwg",
    "validated_by_safety_plane", "emits_metric_event",
]

print(f"\n{'Edge Type':<40s} {'Count':>8s} {'Modules':>8s}")
print("-" * 58)
for t in types:
    cnt = conn.execute(
        "SELECT COUNT(*) FROM edges WHERE relation_type=?", (t,)
    ).fetchone()[0]
    mods = conn.execute(
        "SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type=?", (t,)
    ).fetchone()[0]
    marker = " <-- DENOM" if t in ("writes_to", "reads_from", "records_execution_trace", "calls", "applies_guardrail") else ""
    print(f"  {t:<38s} {cnt:>8,} {mods:>8,}{marker}")

# Key ratios
print("\n=== KEY RATIOS ===")
ratios = [
    ("reads_through", "reads_from"),
    ("writes_through", "writes_to"),
    ("records_execution_trace", "calls"),
    ("pulls_context", "records_execution_trace"),
    ("emits_determinism_digest", "records_execution_trace"),
    ("signs_execution_trace", "records_execution_trace"),
    ("validated_by_safety_plane", "applies_guardrail"),
    ("emits_metric_event", "records_execution_trace"),
    ("routes_through", "calls"),
    ("snapshots_state", "calls"),
]
for numer, denom in ratios:
    n = conn.execute("SELECT COUNT(*) FROM edges WHERE relation_type=?", (numer,)).fetchone()[0]
    d = conn.execute("SELECT COUNT(*) FROM edges WHERE relation_type=?", (denom,)).fetchone()[0]
    pct = n / d * 100 if d else 0
    print(f"  {numer}/{denom}: {n:,}/{d:,} = {pct:.2f}%")

conn.close()
