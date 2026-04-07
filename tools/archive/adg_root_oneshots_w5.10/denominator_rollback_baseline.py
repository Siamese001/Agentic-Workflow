"""Step 2: Capture pre-rollback denominator baseline from canonical SQLite."""
import glob
import json
import os
import sqlite3

ADG_DIR = r"C:\Git\Agentic-Workflow\artifacts\adg"
OUT_DIR = r"C:\Git\Agentic-Workflow\artifacts\governance"

# Find latest SQLite
pattern = os.path.join(ADG_DIR, "adg_indexed_*.sqlite")
files = sorted(glob.glob(pattern))
if not files:
    raise FileNotFoundError(f"No SQLite found matching {pattern}")
db_path = files[-1]
print(f"Using: {db_path}")

os.makedirs(OUT_DIR, exist_ok=True)

conn = sqlite3.connect(db_path)

# --- Denominator base edges ---
base_query = """
SELECT relation_type, COUNT(*)
FROM edges
WHERE relation_type IN ('writes_to','reads_from','records_execution_trace','calls')
GROUP BY relation_type
"""
base_rows = conn.execute(base_query).fetchall()
base_counts = dict(base_rows)
print("\n=== PRE-ROLLBACK DENOMINATOR COUNTS ===")
for rt, cnt in sorted(base_counts.items()):
    print(f"  {rt}: {cnt}")

# --- Governance numerator edges (for preservation check) ---
gov_query = """
SELECT relation_type, COUNT(*)
FROM edges
WHERE relation_type IN (
    'writes_through','reads_through','pulls_context',
    'emits_determinism_digest','applies_guardrail','emits_metric_event',
    'signs_execution_trace','snapshots_state','emits_replay_key',
    'validated_by_safety_plane','execution_terminates_at_uwg'
)
GROUP BY relation_type
"""
gov_rows = conn.execute(gov_query).fetchall()
gov_counts = dict(gov_rows)
print("\n=== GOVERNANCE NUMERATOR COUNTS (preserve these) ===")
for rt, cnt in sorted(gov_counts.items()):
    print(f"  {rt}: {cnt}")

# --- Total edges ---
total = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
total_nodes = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
print(f"\nTotal edges: {total}")
print(f"Total nodes: {total_nodes}")

# --- All relation types for context ---
all_types = conn.execute(
    "SELECT relation_type, COUNT(*) FROM edges GROUP BY relation_type ORDER BY COUNT(*) DESC",
).fetchall()
print("\n=== ALL RELATION TYPES ===")
for rt, cnt in all_types:
    print(f"  {rt}: {cnt}")

conn.close()

# Save snapshot
snapshot = {
    "sqlite_path": db_path,
    "base_denominators": base_counts,
    "governance_numerators": gov_counts,
    "total_edges": total,
    "total_nodes": total_nodes,
    "all_relation_types": dict(all_types),
}
out_path = os.path.join(OUT_DIR, "pre_denominator_snapshot.json")
with open(out_path, "w") as f:
    json.dump(snapshot, f, indent=2)
print(f"\nSnapshot saved to: {out_path}")
