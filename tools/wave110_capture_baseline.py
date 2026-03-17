"""Wave 110: Capture post-normalization baseline for closure waves.

Records all edge counts from the 1759 SQLite as the locked baseline.
Subsequent closure waves must not increase any denominator.
"""
import glob
import json
import os
import sqlite3
from datetime import datetime

ADG_DIR = r"C:\Git\Agentic-Workflow\artifacts\adg"
files = sorted(glob.glob(os.path.join(ADG_DIR, "adg_indexed_*.sqlite")))
db_path = files[-1]
print(f"Using: {db_path}")

conn = sqlite3.connect(db_path)

# Capture all relation type counts
rows = conn.execute(
    "SELECT relation_type, COUNT(*) FROM edges GROUP BY relation_type ORDER BY COUNT(*) DESC"
).fetchall()

relation_counts = {rt: cnt for rt, cnt in rows}

# Total counts
total_edges = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
total_nodes = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]

# Key denominators
denominators = {
    "calls": relation_counts.get("calls", 0),
    "reads_from": relation_counts.get("reads_from", 0),
    "writes_to": relation_counts.get("writes_to", 0),
    "records_execution_trace": relation_counts.get("records_execution_trace", 0),
}

# Key numerators
numerators = {
    "writes_through": relation_counts.get("writes_through", 0),
    "reads_through": relation_counts.get("reads_through", 0),
    "routes_through": relation_counts.get("routes_through", 0),
    "pulls_context": relation_counts.get("pulls_context", 0),
    "emits_determinism_digest": relation_counts.get("emits_determinism_digest", 0),
    "signs_execution_trace": relation_counts.get("signs_execution_trace", 0),
    "applies_guardrail": relation_counts.get("applies_guardrail", 0),
    "snapshots_state": relation_counts.get("snapshots_state", 0),
    "emits_replay_key": relation_counts.get("emits_replay_key", 0),
    "execution_terminates_at_uwg": relation_counts.get("execution_terminates_at_uwg", 0),
    "validated_by_safety_plane": relation_counts.get("validated_by_safety_plane", 0),
    "emits_metric_event": relation_counts.get("emits_metric_event", 0),
}

baseline = {
    "timestamp": datetime.now().isoformat(),
    "source_sqlite": os.path.basename(db_path),
    "wave": "110_post_normalization",
    "total_edges": total_edges,
    "total_nodes": total_nodes,
    "denominators": denominators,
    "numerators": numerators,
    "all_relation_types": relation_counts,
}

out_path = r"C:\Git\Agentic-Workflow\artifacts\governance\post_normalization_baseline.json"
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, "w") as f:
    json.dump(baseline, f, indent=2)

print(f"\nBaseline saved to: {out_path}")
print(f"\nTotal edges: {total_edges:,}")
print(f"Total nodes: {total_nodes:,}")
print("\n--- Locked Denominators ---")
for k, v in denominators.items():
    print(f"  {k}: {v:,}")
print("\n--- Governance Numerators ---")
for k, v in numerators.items():
    print(f"  {k}: {v:,}")

# Key ratios
print("\n--- Key Ratios ---")
ratios = [
    ("writes_through / writes_to", "writes_through", "writes_to"),
    ("reads_through / reads_from", "reads_through", "reads_from"),
    ("pulls_context / records_execution_trace", "pulls_context", "records_execution_trace"),
    ("emits_determinism_digest / records_execution_trace", "emits_determinism_digest", "records_execution_trace"),
    ("records_execution_trace / calls", "records_execution_trace", "calls"),
    ("validated_by_safety_plane / applies_guardrail", "validated_by_safety_plane", "applies_guardrail"),
]
for label, num, den in ratios:
    n = numerators.get(num, denominators.get(num, 0))
    d = denominators.get(den, numerators.get(den, 0))
    pct = n / d * 100 if d > 0 else 0
    print(f"  {label}: {n:,} / {d:,} = {pct:.1f}%")

conn.close()
